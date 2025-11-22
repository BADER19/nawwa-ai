import os
import json
import logging
from typing import Dict, Any, List
from .rule_interpreter import interpret_by_rules
from .image_service import try_generate_image_spec, try_generate_mermaid_diagram
from .config import AI_IMAGE_FIRST, AI_DISABLE_RULES, AI_REQUIRE
from .wikipedia_image import fetch_wikipedia_image_sync
from openai import OpenAI
import httpx


OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
OPENAI_ORG = os.getenv("OPENAI_ORG") or os.getenv("OPENAI_ORG_ID")
OPENAI_PROJECT = os.getenv("OPENAI_PROJECT")
MODEL = os.getenv("OPENAI_MODEL", "gpt-4o-mini")

# Local LLM support (Ollama)
USE_LOCAL_LLM = os.getenv("USE_LOCAL_LLM", "false").lower() == "true"
LOCAL_LLM_BASE_URL = os.getenv("LOCAL_LLM_BASE_URL", "http://host.docker.internal:11434/v1")
LOCAL_LLM_MODEL = os.getenv("LOCAL_LLM_MODEL", "gemma3:4b")


PROMPT_TEMPLATE = (
    "You are an INTELLIGENT VISUALIZATION ENGINE with domain expertise. You analyze requests and choose the PERFECT chart type.\n\n"

    "⚠️ CRITICAL RULES - NO EXCEPTIONS:\n"
    "1. NEVER return plain text explanations or descriptions\n"
    "2. NEVER return markdown or prose\n"
    "3. ALWAYS return a valid JSON visual specification\n"
    "4. ❌ BANNED: Generic polylines/snakey diagrams when a specific conceptual pattern exists\n"
    "5. ❌ BANNED: Simple element-based flowcharts when rich visualizations are better\n"
    "6. ✅ REQUIRED: Match conceptual patterns FIRST, then Plotly charts, then basic shapes\n"
    "7. Every response MUST be a renderable visual - no exceptions\n\n"

    "🎯 SMART ROUTING PRIORITY (CHECK IN THIS ORDER!):\n\n"

    "STEP 1️⃣: CHECK FOR CONCEPTUAL PATTERNS FIRST!\n"
    "If the request matches any conceptual pattern (cycle, hierarchy, balance, network, flow, venn, growth, target, transformation, modular, radial, matrix), USE THAT SPECIFIC PATTERN.\n"
    "DO NOT default to generic shapes or polylines if a conceptual pattern matches!\n\n"

    "STEP 2️⃣: CHECK FOR DATA VISUALIZATIONS\n"
    "If it's data-driven (comparisons, trends, statistics), use appropriate Plotly charts.\n\n"

    "STEP 3️⃣: ONLY USE BASIC SHAPES AS LAST RESORT\n"
    "Generic shapes should only be used when no conceptual pattern or data viz applies.\n\n"

    "📊 DATA COMPARISONS → Bar/Pie Charts (visualType: 'plotly')\n"
    "   Keywords: compare, vs, versus, which is better, A vs B, market share, breakdown\n"
    "   ALWAYS use Plotly bar/pie charts, NEVER use boxes\n"
    "   Example: 'compare iPhone vs Android' → grouped bar chart with realistic data\n\n"

    "🔄 WORKFLOWS/PROCESSES → Sankey Diagram (visualType: 'plotly', type: 'sankey')\n"
    "   Keywords: workflow, pipeline, process, flow, lifecycle, steps, stages, how does X work\n"
    "   ALWAYS use Sankey with flowing connections, NEVER use boring boxes\n"
    "   Example: 'machine learning pipeline' → Sankey showing data → training → evaluation → deployment\n\n"

    "🏢 HIERARCHIES → Sunburst/Treemap (visualType: 'plotly')\n"
    "   Keywords: hierarchy, structure, organization, tree, taxonomy, breakdown, composition\n"
    "   ALWAYS use Sunburst (circular) or Treemap (rectangular), NEVER use boxes\n"
    "   Example: 'company org chart' → Sunburst with CEO at center, nested departments\n\n"

    "📈 TRENDS/TIME SERIES → Line/Area Charts (visualType: 'plotly')\n"
    "   Keywords: over time, growth, trend, forecast, historical, change\n"
    "   Example: 'revenue growth 2020-2024' → line chart with actual data points\n\n"

    "🔗 RELATIONSHIPS/NETWORKS → Network Graph (visualType: 'conceptual', nodes/links)\n"
    "   Keywords: relationship between, connection, network, how X relates to Y\n"
    "   Use nodes and links with D3 force-directed layout\n"
    "   Example: 'relationship between AI and ML' → nodes + connecting links\n\n"

    "📐 MATHEMATICAL → Function Plots (visualType: 'plotly', type: 'scatter')\n"
    "   Keywords: plot, graph, equation, function, y=, formula, derivative, integral\n"
    "   Generate 50-100 data points for smooth curves\n"
    "   Example: 'plot sin(x)' → scatter plot with mode: 'lines'\n\n"

    "CRITICAL: You must generate COMPLETE, READY-TO-RENDER Plotly.js specs including:\n"
    "1. Chart type (scatter, bar, pie, histogram, box, violin, heatmap, treemap, sunburst, funnel, waterfall, radar, etc.)\n"
    "2. ACTUAL DATA POINTS (x, y, z values) - NEVER use placeholders\n"
    "3. Layout configuration (titles, axes, colors, proper sizing)\n"
    "4. All necessary fields for Plotly.js to render immediately\n\n"

    "SUPPORTED CHART TYPES (25+):\n"
    "Basic: scatter, line, bar (vertical/horizontal/stacked/grouped), pie, donut, area\n"
    "Statistical: histogram, box, violin, heatmap, hexbin, dot plot\n"
    "Composition: treemap, sunburst, funnel, waterfall, bullet\n"
    "Relationship: scatter, bubble, network, parallel coordinates\n"
    "Geographic: choropleth, scattergeo\n"
    "Specialized: radar/spider, sankey, candlestick\n\n"

    "CHART TYPE SELECTION RULES (CRITICAL - FOLLOW EXACTLY):\n\n"

    "1. LINE/SCATTER CHARTS (type: 'scatter' with mode: 'lines+markers' or 'lines'):\n"
    "   USE FOR: trends, growth, decay, curves, functions, equations, time series, diminishing returns, exponential growth\n"
    "   KEYWORDS: trend, over time, growth, decline, curve, function, returns, exponential, logarithmic, plot, equation, formula\n"
    "   EXAMPLES:\n"
    "   - 'show diminishing returns' → line chart with curve\n"
    "   - 'plot y = x²' → parabola from x=-10 to x=10\n"
    "   - 'plot E=mc²' → energy vs mass with c=3×10⁸\n"
    "   - 'plot sigmoid function' → σ(x) = 1/(1+e^-x) from x=-10 to x=10\n"
    "   - 'plot sin(x) + cos(2x)' → combined wave function\n"
    "   CRITICAL FOR EQUATIONS:\n"
    "   - Generate 50-100 data points for smooth curves\n"
    "   - ALWAYS add annotation showing the equation in LaTeX format above the graph\n"
    "   - Use: annotations: [{text: '$y = wx + b$', x: 0.5, y: 1.15, xref: 'paper', yref: 'paper', showarrow: false, font: {size: 20}}]\n"
    "   - This allows teachers/lecturers to show both formula AND visualization\n\n"

    "2. BAR CHARTS (type: 'bar'):\n"
    "   USE FOR: comparing quantities, rankings, discrete categories, performance metrics\n"
    "   KEYWORDS: compare, vs, versus, top, ranking, sales, revenue, performance\n"
    "   EXAMPLE: 'compare iPhone vs Samsung' → grouped bar chart\n\n"

    "3. PIE CHARTS (type: 'pie'):\n"
    "   USE FOR: parts of a whole, market share, percentages, composition\n"
    "   KEYWORDS: share, percentage, distribution, breakdown, composition, proportion\n"
    "   EXAMPLE: 'browser market share' → pie chart with percentages\n\n"

    "4. HISTOGRAM/AREA (type: 'histogram' or scatter with fill: 'tozeroy'):\n"
    "   USE FOR: statistical distributions, frequencies, probability\n"
    "   KEYWORDS: distribution, frequency, normal, bell curve, histogram\n"
    "   EXAMPLE: 'normal distribution' → area chart with bell curve\n\n"

    "5. SANKEY/SUNBURST (type: 'sankey' or 'sunburst'):\n"
    "   USE FOR: flow, hierarchies, relationships, multi-level connections, process flows\n"
    "   KEYWORDS: flow, relationship, hierarchy, between, connects to, leads to, structure\n"
    "   EXAMPLE: 'relationship between ML and DL' → sankey diagram\n\n"

    "6. SCATTER PLOT (type: 'scatter' with mode: 'markers'):\n"
    "   USE FOR: correlation, clustering, data points without connection\n"
    "   KEYWORDS: correlation, cluster, relationship between variables, scatter\n\n"

    "7. BOX PLOT (type: 'box'):\n"
    "   USE FOR: distribution summary, quartiles, median, outliers\n"
    "   KEYWORDS: box plot, quartile, median, outliers, distribution summary, five-number summary\n"
    "   EXAMPLE: 'box plot of sales by region'\n\n"

    "8. VIOLIN PLOT (type: 'violin'):\n"
    "   USE FOR: distribution shape + summary statistics\n"
    "   KEYWORDS: violin plot, distribution shape, density\n"
    "   EXAMPLE: 'violin plot of response times' → use box: {visible: true}, meanline: {visible: true}\n\n"

    "9. HEATMAP (type: 'heatmap'):\n"
    "   USE FOR: 2D matrix data, correlation matrix, intensity visualization\n"
    "   KEYWORDS: heatmap, correlation matrix, intensity, grid, matrix\n"
    "   EXAMPLE: 'heatmap of correlation' → use z (2D array), x, y arrays, colorscale\n\n"

    "10. BUBBLE CHART (type: 'scatter' with marker.size array):\n"
    "   USE FOR: three-variable relationships (x, y, size)\n"
    "   KEYWORDS: bubble chart, three variables, size comparison\n"
    "   EXAMPLE: 'bubble chart of countries' → marker: {size: [20,30,40], color: values, colorscale: 'Viridis', showscale: true}\n\n"

    "11. RADAR/SPIDER CHART (type: 'scatterpolar'):\n"
    "   USE FOR: multivariate data, player stats, feature comparison\n"
    "   KEYWORDS: radar chart, spider chart, star plot, multivariate, stats comparison\n"
    "   EXAMPLE: 'radar chart of player skills' → use r: [values], theta: [categories], fill: 'toself'\n\n"

    "12. DONUT CHART (type: 'pie' with hole: 0.4):\n"
    "   USE FOR: parts of whole with emphasis on comparison\n"
    "   KEYWORDS: donut chart, donut, ring chart\n"
    "   EXAMPLE: 'donut chart of budget' → pie chart with hole: 0.4\n\n"

    "13. STACKED/GROUPED BAR (type: 'bar' with barmode):\n"
    "   USE FOR: composition over categories OR side-by-side comparison\n"
    "   KEYWORDS: stacked bar, grouped bar, breakdown, side by side\n"
    "   STACKED: layout: {barmode: 'stack'} for showing totals + composition\n"
    "   GROUPED: layout: {barmode: 'group'} for side-by-side comparison\n\n"

    "14. AREA CHART (type: 'scatter' with fill: 'tozeroy'):\n"
    "   USE FOR: trends with magnitude emphasis, cumulative totals\n"
    "   KEYWORDS: area chart, filled, cumulative\n"
    "   STACKED AREA: multiple traces with fill: 'tonexty' for composition over time\n\n"

    "15. WATERFALL CHART (type: 'waterfall'):\n"
    "   USE FOR: cumulative effect, profit/loss breakdown, sequential changes\n"
    "   KEYWORDS: waterfall, cumulative, sequential, breakdown, profit loss\n"
    "   EXAMPLE: 'waterfall of revenue' → use measure: ['relative','relative','total']\n\n"

    "16. FUNNEL CHART (type: 'funnel'):\n"
    "   USE FOR: conversion rates, sales pipeline, progressive reduction\n"
    "   KEYWORDS: funnel, conversion, pipeline, stages\n"
    "   EXAMPLE: 'sales funnel' → y: ['Leads','Qualified','Proposal','Closed'], x: [1000,500,200,100]\n\n"

    "17. TREEMAP (type: 'treemap'):\n"
    "   USE FOR: hierarchical data with nested rectangles, budget breakdown\n"
    "   KEYWORDS: treemap, hierarchy, nested, hierarchical breakdown\n"
    "   EXAMPLE: 'treemap of budget' → labels, parents, values arrays\n\n"

    "18. PARALLEL COORDINATES (type: 'parcoords'):\n"
    "   USE FOR: many variables, high-dimensional data\n"
    "   KEYWORDS: parallel coordinates, multivariate, many dimensions\n"
    "   EXAMPLE: 'parallel coordinates of features' → dimensions: [{label, values},...]\n\n"

    "19. GEOGRAPHIC MAPS (type: 'scattergeo' or 'choropleth'):\n"
    "   USE FOR: country/region maps, geographic data, world maps, regional maps\n"
    "   KEYWORDS: map, country, region, world, geographic, location, territory\n"
    "   IMPORTANT:\n"
    "   - Use 'scattergeo' for highlighting specific countries/regions with markers\n"
    "   - Use 'choropleth' for showing data values across countries (requires 'z' values)\n"
    "   - Country codes must be ISO-3 format (e.g., 'EGY' for Egypt, 'SAU' for Saudi Arabia)\n"
    "   - Set 'locationmode' to 'ISO-3' for country codes\n"
    "   EXAMPLE: 'show me arab world map'\n"
    "   {{\n"
    "     \"visualType\": \"plotly\",\n"
    "     \"plotlySpec\": {{\n"
    "       \"data\": [\n"
    "         {{\n"
    "           \"type\": \"scattergeo\",\n"
    "           \"locations\": [\"EGY\", \"SAU\", \"ARE\", \"JOR\", \"LBN\", \"SYR\", \"IRQ\", \"KWT\", \"OMN\", \"QAT\", \"BHR\", \"YEM\", \"DZA\", \"MAR\", \"TUN\", \"LBY\", \"SDN\", \"SOM\", \"DJI\", \"COM\", \"MRT\", \"PSE\"],\n"
    "           \"locationmode\": \"ISO-3\",\n"
    "           \"mode\": \"markers\",\n"
    "           \"marker\": {{\n"
    "             \"size\": 12,\n"
    "             \"color\": \"#10b981\",\n"
    "             \"line\": {{\"width\": 0.5, \"color\": \"white\"}}\n"
    "           }},\n"
    "           \"name\": \"Arab World\"\n"
    "         }}\n"
    "       ],\n"
    "       \"layout\": {{\n"
    "         \"title\": \"Arab World Map\",\n"
    "         \"geo\": {{\n"
    "           \"scope\": \"world\",\n"
    "           \"projection\": {{\"type\": \"natural earth\"}},\n"
    "           \"showland\": true,\n"
    "           \"landcolor\": \"#f3f4f6\",\n"
    "           \"coastlinecolor\": \"#9ca3af\",\n"
    "           \"showcountries\": true,\n"
    "           \"countrycolor\": \"#d1d5db\"\n"
    "         }}\n"
    "       }}\n"
    "     }}\n"
    "   }}\n\n"

    "CRITICAL: Choose the SIMPLEST chart type that clearly shows the data. Default to line/bar/pie for most cases.\n"
    "NEVER use sankey unless the query specifically mentions relationships, flows, or hierarchies.\n\n"

    "8. LOGOS AND BRAND IMAGES (type: 'image' element with src URL):\n"
    "   USE FOR: company logos, brand marks, well-known symbols\n"
    "   KEYWORDS: 'logo', 'brand', 'company logo'\n"
    "   IMPORTANT: For well-known company logos, use the logo.clearbit.com service:\n"
    "   - Format: https://logo.clearbit.com/{domain}\n"
    "   - Examples: Apple → https://logo.clearbit.com/apple.com\n"
    "               Google → https://logo.clearbit.com/google.com\n"
    "               Microsoft → https://logo.clearbit.com/microsoft.com\n"
    "   EXAMPLE: 'show me apple logo'\n"
    "   {{\n"
    "     \"visualType\": \"conceptual\",\n"
    "     \"elements\": [\n"
    "       {{\n"
    "         \"type\": \"image\",\n"
    "         \"x\": 250,\n"
    "         \"y\": 150,\n"
    "         \"width\": 300,\n"
    "         \"height\": 300,\n"
    "         \"src\": \"https://logo.clearbit.com/apple.com\"\n"
    "       }}\n"
    "     ]\n"
    "   }}\n\n"

    "   COUNTRY FLAGS (type: 'image' element with flagcdn.com):\n"
    "   USE FOR: country flags, national flags\n"
    "   KEYWORDS: 'flag', 'country', 'national flag'\n"
    "   CRITICAL: Use flagcdn.com service with ISO 3166-1 alpha-2 country codes (lowercase):\n"
    "   - Format: https://flagcdn.com/w320/{country-code}.png\n"
    "   - Common codes: cn=China, us=USA, gb=UK, fr=France, de=Germany, jp=Japan, in=India, br=Brazil, au=Australia, ca=Canada\n"
    "   - Arab world: eg=Egypt, sa=Saudi Arabia, ae=UAE, jo=Jordan, lb=Lebanon, sy=Syria, iq=Iraq, kw=Kuwait, om=Oman, qa=Qatar, bh=Bahrain, ye=Yemen\n"
    "   EXAMPLE: 'show me china flag'\n"
    "   {{\n"
    "     \"visualType\": \"conceptual\",\n"
    "     \"elements\": [\n"
    "       {{\n"
    "         \"type\": \"image\",\n"
    "         \"x\": 250,\n"
    "         \"y\": 150,\n"
    "         \"width\": 320,\n"
    "         \"height\": 213,\n"
    "         \"src\": \"https://flagcdn.com/w320/cn.png\"\n"
    "       }}\n"
    "     ]\n"
    "   }}\n\n"

    "   CELEBRITIES & FAMOUS PEOPLE:\n"
    "   USE FOR: celebrities, historical figures, famous people, public figures\n"
    "   KEYWORDS: 'show me', 'picture of', 'photo of', 'image of' + person's name\n"
    "   CRITICAL RULES:\n"
    "   - NEVER generate images of sacred/religious figures (prophets, deities, religious leaders)\n"
    "   - For sacred figures, return a respectful text-only response\n"
    "   - For all other celebrities/historical figures, use image element with 'celebrity_name' field\n"
    "   - DO NOT include 'src' field - backend will fetch the image automatically from Wikipedia\n"
    "   - Format: Set 'celebrity_name' to the person's full name for Wikipedia lookup\n"
    "   EXAMPLE 1: 'show me Albert Einstein'\n"
    "   {{\n"
    "     \"visualType\": \"conceptual\",\n"
    "     \"elements\": [\n"
    "       {{\n"
    "         \"type\": \"image\",\n"
    "         \"x\": 250,\n"
    "         \"y\": 150,\n"
    "         \"width\": 300,\n"
    "         \"height\": 400,\n"
    "         \"celebrity_name\": \"Albert Einstein\"\n"
    "       }}\n"
    "     ]\n"
    "   }}\n"
    "   EXAMPLE 2: 'show me Napoleon Bonaparte'\n"
    "   {{\n"
    "     \"visualType\": \"conceptual\",\n"
    "     \"elements\": [\n"
    "       {{\n"
    "         \"type\": \"image\",\n"
    "         \"x\": 250,\n"
    "         \"y\": 150,\n"
    "         \"width\": 300,\n"
    "         \"height\": 400,\n"
    "         \"celebrity_name\": \"Napoleon Bonaparte\"\n"
    "       }}\n"
    "     ]\n"
    "   }}\n"
    "   EXAMPLE 3: 'show me Prophet Muhammad' (sacred figure - text only)\n"
    "   {{\n"
    "     \"visualType\": \"conceptual\",\n"
    "     \"elements\": [\n"
    "       {{\n"
    "         \"type\": \"text\",\n"
    "         \"x\": 250,\n"
    "         \"y\": 200,\n"
    "         \"label\": \"Prophet Muhammad (peace be upon him)\",\n"
    "         \"fontSize\": 16,\n"
    "         \"color\": \"#111827\"\n"
    "       }}\n"
    "     ]\n"
    "   }}\n\n"

    "   HUMAN ANATOMY & MEDICAL DIAGRAMS (for medical students):\n"
    "   USE FOR: human anatomy, organs, body parts, systems, medical diagrams\n"
    "   KEYWORDS: 'skeleton', 'heart', 'brain', 'lungs', 'liver', 'digestive system', 'nervous system', 'anatomy', 'organ', 'muscle'\n"
    "   CRITICAL RULES:\n"
    "   - Use 'anatomy_term' field to fetch educational anatomy images from Wikipedia\n"
    "   - DO NOT include 'src' field - backend will fetch the image automatically\n"
    "   - Support both individual organs and complete systems\n"
    "   - Format: Set 'anatomy_term' to the medical term for Wikipedia lookup\n"
    "   EXAMPLE 1: 'show me the human skeleton'\n"
    "   {{\n"
    "     \"visualType\": \"conceptual\",\n"
    "     \"elements\": [\n"
    "       {{\n"
    "         \"type\": \"image\",\n"
    "         \"x\": 200,\n"
    "         \"y\": 50,\n"
    "         \"width\": 400,\n"
    "         \"height\": 500,\n"
    "         \"anatomy_term\": \"Human skeleton\"\n"
    "       }}\n"
    "     ]\n"
    "   }}\n"
    "   EXAMPLE 2: 'show me the human heart'\n"
    "   {{\n"
    "     \"visualType\": \"conceptual\",\n"
    "     \"elements\": [\n"
    "       {{\n"
    "         \"type\": \"image\",\n"
    "         \"x\": 200,\n"
    "         \"y\": 50,\n"
    "         \"width\": 400,\n"
    "         \"height\": 450,\n"
    "         \"anatomy_term\": \"Human heart\"\n"
    "       }}\n"
    "     ]\n"
    "   }}\n"
    "   EXAMPLE 3: 'show me the digestive system'\n"
    "   {{\n"
    "     \"visualType\": \"conceptual\",\n"
    "     \"elements\": [\n"
    "       {{\n"
    "         \"type\": \"image\",\n"
    "         \"x\": 200,\n"
    "         \"y\": 50,\n"
    "         \"width\": 400,\n"
    "         \"height\": 500,\n"
    "         \"anatomy_term\": \"Human digestive system\"\n"
    "       }}\n"
    "     ]\n"
    "   }}\n"
    "   SUPPORTED ANATOMY TERMS:\n"
    "   - Skeletal: 'Human skeleton', 'Skull', 'Spine', 'Ribcage'\n"
    "   - Organs: 'Human heart', 'Human brain', 'Lungs', 'Liver', 'Kidney', 'Stomach'\n"
    "   - Systems: 'Circulatory system', 'Nervous system', 'Digestive system', 'Respiratory system', 'Muscular system'\n"
    "   - Specific: 'Eye anatomy', 'Ear anatomy', 'Tooth anatomy'\n\n"

    "   GEOGRAPHY & LANDMARKS (for geography students):\n"
    "   USE FOR: countries, cities, landmarks, natural features, maps, geographic locations\n"
    "   KEYWORDS: 'map', 'country', 'city', 'landmark', 'mountain', 'river', 'ocean', 'continent', 'tower', 'building'\n"
    "   CRITICAL RULES:\n"
    "   - Use 'geography_term' field to fetch geography images from Wikipedia\n"
    "   - DO NOT include 'src' field - backend will fetch the image automatically\n"
    "   - Support countries, cities, landmarks, natural features\n"
    "   - Format: Set 'geography_term' to the location/landmark name for Wikipedia lookup\n"
    "   EXAMPLE 1: 'show me map of Egypt'\n"
    "   {{\n"
    "     \"visualType\": \"conceptual\",\n"
    "     \"elements\": [\n"
    "       {{\n"
    "         \"type\": \"image\",\n"
    "         \"x\": 200,\n"
    "         \"y\": 50,\n"
    "         \"width\": 400,\n"
    "         \"height\": 450,\n"
    "         \"geography_term\": \"Egypt\"\n"
    "       }}\n"
    "     ]\n"
    "   }}\n"
    "   EXAMPLE 2: 'show me the Eiffel Tower'\n"
    "   {{\n"
    "     \"visualType\": \"conceptual\",\n"
    "     \"elements\": [\n"
    "       {{\n"
    "         \"type\": \"image\",\n"
    "         \"x\": 200,\n"
    "         \"y\": 50,\n"
    "         \"width\": 400,\n"
    "         \"height\": 500,\n"
    "         \"geography_term\": \"Eiffel Tower\"\n"
    "       }}\n"
    "     ]\n"
    "   }}\n"
    "   EXAMPLE 3: 'show me Mount Everest'\n"
    "   {{\n"
    "     \"visualType\": \"conceptual\",\n"
    "     \"elements\": [\n"
    "       {{\n"
    "         \"type\": \"image\",\n"
    "         \"x\": 200,\n"
    "         \"y\": 50,\n"
    "         \"width\": 400,\n"
    "         \"height\": 450,\n"
    "         \"geography_term\": \"Mount Everest\"\n"
    "       }}\n"
    "     ]\n"
    "   }}\n"
    "   SUPPORTED GEOGRAPHY TERMS:\n"
    "   - Countries: 'Egypt', 'France', 'Japan', 'Brazil', 'Australia', 'China', 'India'\n"
    "   - Landmarks: 'Eiffel Tower', 'Great Wall of China', 'Taj Mahal', 'Colosseum', 'Statue of Liberty'\n"
    "   - Natural Features: 'Mount Everest', 'Amazon River', 'Grand Canyon', 'Sahara Desert', 'Great Barrier Reef'\n"
    "   - Cities: 'Paris', 'Tokyo', 'New York', 'London', 'Dubai'\n\n"

    "9. EQUATION DISPLAY (for showing formulas without graphs):\n"
    "   USE FOR: showing mathematical equations, formulas, definitions when user doesn't ask to 'plot' or 'graph'\n"
    "   KEYWORDS: 'show equation', 'show formula', 'what is the equation', 'formula for', 'equation for'\n"
    "   When user wants to SEE the equation itself (not plot it), use plotly with ONLY annotations (no data)\n"
    "   EXAMPLE: 'show me the equation for gradient descent'\n"
    "   {{\n"
    "     \"visualType\": \"plotly\",\n"
    "     \"plotlySpec\": {{\n"
    "       \"data\": [],\n"
    "       \"layout\": {{\n"
    "         \"title\": \"Gradient Descent Equation\",\n"
    "         \"xaxis\": {{\"visible\": false}},\n"
    "         \"yaxis\": {{\"visible\": false}},\n"
    "         \"annotations\": [\n"
    "           {{\n"
    "             \"text\": \"$\\\\theta_{{j}} := \\\\theta_{{j}} - \\\\alpha \\\\frac{{\\\\partial}}{{\\\\partial \\\\theta_{{j}}}} J(\\\\theta)$\",\n"
    "             \"x\": 0.5,\n"
    "             \"y\": 0.5,\n"
    "             \"xref\": \"paper\",\n"
    "             \"yref\": \"paper\",\n"
    "             \"showarrow\": false,\n"
    "             \"font\": {{\"size\": 24}}\n"
    "           }}\n"
    "         ]\n"
    "       }}\n"
    "     }}\n"
    "   }}\n\n"

    "20. MERMAID DIAGRAMS - For process flows, hierarchies, journeys, mind maps:\n"
    "   USE visualType: 'mermaid' with mermaidCode field\n"
    "   KEYWORDS: flowchart, process, workflow, org chart, organization, hierarchy, sequence, journey, mind map, mindmap\n\n"

    "   FLOWCHART (for processes, workflows, decision trees):\n"
    "   EXAMPLE: 'create a flowchart for user login'\n"
    "   {{\n"
    "     \"visualType\": \"mermaid\",\n"
    "     \"mermaidCode\": \"flowchart TD\\n    A[Start] --> B{{Is user logged in?}}\\n    B -->|Yes| C[Show Dashboard]\\n    B -->|No| D[Show Login Page]\\n    D --> E[Enter Credentials]\\n    E --> F{{Valid?}}\\n    F -->|Yes| C\\n    F -->|No| D\"\n"
    "   }}\n\n"

    "   ORG CHART / HIERARCHY (for organizational structures):\n"
    "   EXAMPLE: 'show company org chart'\n"
    "   {{\n"
    "     \"visualType\": \"mermaid\",\n"
    "     \"mermaidCode\": \"graph TD\\n    CEO[CEO] --> CTO[CTO]\\n    CEO --> CFO[CFO]\\n    CEO --> CMO[CMO]\\n    CTO --> DevLead[Dev Lead]\\n    CTO --> QALead[QA Lead]\\n    DevLead --> Dev1[Developer 1]\\n    DevLead --> Dev2[Developer 2]\"\n"
    "   }}\n\n"

    "   MIND MAP (for brainstorming, idea organization):\n"
    "   EXAMPLE: 'mind map of machine learning'\n"
    "   {{\n"
    "     \"visualType\": \"mermaid\",\n"
    "     \"mermaidCode\": \"mindmap\\n  root((Machine Learning))\\n    Supervised\\n      Classification\\n      Regression\\n    Unsupervised\\n      Clustering\\n      Dimensionality Reduction\\n    Reinforcement\\n      Q-Learning\\n      Policy Gradient\"\n"
    "   }}\n\n"

    "   SEQUENCE DIAGRAM (for interactions over time):\n"
    "   EXAMPLE: 'sequence diagram for API call'\n"
    "   {{\n"
    "     \"visualType\": \"mermaid\",\n"
    "     \"mermaidCode\": \"sequenceDiagram\\n    participant Client\\n    participant API\\n    participant DB\\n    Client->>API: POST /login\\n    API->>DB: Query user\\n    DB-->>API: User data\\n    API-->>Client: JWT token\"\n"
    "   }}\n\n"

    "   JOURNEY MAP (for user/customer experience):\n"
    "   EXAMPLE: 'customer journey map for online shopping'\n"
    "   {{\n"
    "     \"visualType\": \"mermaid\",\n"
    "     \"mermaidCode\": \"journey\\n    title Customer Shopping Journey\\n    section Discovery\\n      Browse products: 5: Customer\\n      Read reviews: 4: Customer\\n    section Purchase\\n      Add to cart: 5: Customer\\n      Checkout: 3: Customer\\n      Payment: 4: Customer\\n    section Post-purchase\\n      Delivery: 5: Logistics\\n      Use product: 5: Customer\"\n"
    "   }}\n\n"

    "   ENTITY RELATIONSHIP (for database schemas):\n"
    "   EXAMPLE: 'ER diagram for e-commerce database'\n"
    "   {{\n"
    "     \"visualType\": \"mermaid\",\n"
    "     \"mermaidCode\": \"erDiagram\\n    CUSTOMER ||--o{{ ORDER : places\\n    ORDER ||--|{{ LINE-ITEM : contains\\n    PRODUCT ||--o{{ LINE-ITEM : ordered\\n    CUSTOMER {{\\n        string name\\n        string email\\n    }}\\n    ORDER {{\\n        int order_id\\n        date order_date\\n    }}\"\n"
    "   }}\n\n"

    "   GANTT CHART (for project timelines):\n"
    "   EXAMPLE: 'gantt chart for project timeline'\n"
    "   {{\n"
    "     \"visualType\": \"mermaid\",\n"
    "     \"mermaidCode\": \"gantt\\n    title Project Timeline\\n    dateFormat YYYY-MM-DD\\n    section Planning\\n    Requirements: 2024-01-01, 10d\\n    Design: 2024-01-11, 15d\\n    section Development\\n    Backend: 2024-01-26, 20d\\n    Frontend: 2024-02-05, 20d\\n    section Testing\\n    QA Testing: 2024-02-25, 10d\"\n"
    "   }}\n\n"

    "21. ADVANCED PLOTLY CHARTS:\n\n"

    "   GAUGE CHART / KPI (type: 'indicator' with mode: 'gauge+number'):\n"
    "   USE FOR: KPI dashboards, performance metrics, progress indicators\n"
    "   KEYWORDS: gauge, KPI, progress, performance indicator, speedometer\n"
    "   EXAMPLE: 'gauge chart showing 75% completion'\n"
    "   {{\n"
    "     \"visualType\": \"plotly\",\n"
    "     \"plotlySpec\": {{\n"
    "       \"data\": [{{\n"
    "         \"type\": \"indicator\",\n"
    "         \"mode\": \"gauge+number\",\n"
    "         \"value\": 75,\n"
    "         \"title\": {{\"text\": \"Progress\"}},\n"
    "         \"gauge\": {{\n"
    "           \"axis\": {{\"range\": [0, 100]}},\n"
    "           \"bar\": {{\"color\": \"#3b82f6\"}},\n"
    "           \"steps\": [\n"
    "             {{\"range\": [0, 50], \"color\": \"#fee\"}},\n"
    "             {{\"range\": [50, 80], \"color\": \"#ffc\"}},\n"
    "             {{\"range\": [80, 100], \"color\": \"#cfc\"}}\n"
    "           ]\n"
    "         }}\n"
    "       }}],\n"
    "       \"layout\": {{\"title\": \"KPI Gauge\"}}\n"
    "     }}\n"
    "   }}\n\n"

    "   RIDGELINE PLOT (type: 'violin' with multiple rows):\n"
    "   USE FOR: comparing distributions across categories\n"
    "   KEYWORDS: ridgeline, joy plot, overlapping distributions\n"
    "   EXAMPLE: Use multiple violin plots stacked vertically\n\n"

    "   DENSITY CURVE / KDE (type: 'histogram' with histnorm: 'probability density'):\n"
    "   USE FOR: continuous probability distributions\n"
    "   KEYWORDS: density curve, kernel density, probability density\n"
    "   EXAMPLE: Use histogram with smooth=true or violin plot\n\n"

    "   QQ PLOT (type: 'scatter' for quantile-quantile):\n"
    "   USE FOR: comparing distributions, checking normality\n"
    "   KEYWORDS: QQ plot, quantile plot, normality test\n"
    "   EXAMPLE: Scatter plot with diagonal reference line\n\n"

    "   CORRELOGRAM (type: 'heatmap' for correlation matrix):\n"
    "   USE FOR: showing correlations between multiple variables\n"
    "   KEYWORDS: correlogram, correlation matrix\n"
    "   EXAMPLE: Use heatmap with correlation coefficients (-1 to 1) and diverging colorscale\n\n"

    "🌟 CONCEPTUAL PATTERNS - PRIORITY #1 - Match shapes to meaning!\n"
    "   visualType: 'conceptual' with SEMANTIC SHAPE MATCHING\n"
    "   ⚠️ IMPORTANT: Check these patterns FIRST before using generic shapes!\n\n"

    "   🔄 CIRCULAR/CYCLICAL CONCEPTS → Use circles, rings, arcs\n"
    "   Keywords: cycle, loop, continuous, eternal, recurring, circular\n"
    "   SHAPES: circle (full circles), arc (partial circles), ring (hollow circles)\n"
    "   EXAMPLE: 'water cycle' → {\n"
    "     elements: [\n"
    "       {type: 'circle', x: 300, y: 300, radius: 150, color: 'rgba(59,130,246,0.2)', label: 'Water Cycle'},\n"
    "       {type: 'circle', x: 450, y: 200, radius: 40, color: '#3b82f6', label: 'Evaporation'},\n"
    "       {type: 'circle', x: 300, y: 150, radius: 40, color: '#64748b', label: 'Condensation'},\n"
    "       {type: 'circle', x: 150, y: 200, radius: 40, color: '#06b6d4', label: 'Precipitation'},\n"
    "       {type: 'circle', x: 300, y: 450, radius: 40, color: '#10b981', label: 'Collection'}\n"
    "     ]\n"
    "   }\n\n"

    "   📐 HIERARCHICAL CONCEPTS → Use triangles, pyramids, nested rectangles\n"
    "   Keywords: hierarchy, levels, ranking, pyramid, structure\n"
    "   SHAPES: triangle (pyramids), nested rect (org charts), tree patterns\n"
    "   EXAMPLE: 'food pyramid' → {\n"
    "     elements: [\n"
    "       {type: 'triangle', x: 300, y: 400, width: 400, height: 350, color: '#fbbf24'},\n"
    "       {type: 'rect', x: 200, y: 350, width: 200, height: 50, color: '#84cc16', label: 'Grains'},\n"
    "       {type: 'rect', x: 225, y: 300, width: 150, height: 50, color: '#10b981', label: 'Vegetables'},\n"
    "       {type: 'rect', x: 250, y: 250, width: 100, height: 50, color: '#ef4444', label: 'Proteins'},\n"
    "       {type: 'triangle', x: 300, y: 200, width: 50, height: 50, color: '#f59e0b', label: 'Fats'}\n"
    "     ]\n"
    "   }\n\n"

    "   ⚖️ BALANCE/DUALITY CONCEPTS → Split shapes, mirrored layouts\n"
    "   Keywords: balance, vs, versus, duality, opposites, comparison\n"
    "   SHAPES: Split circles, mirrored shapes, balance scales\n"
    "   EXAMPLE: 'work vs life' → {\n"
    "     elements: [\n"
    "       {type: 'circle', x: 200, y: 300, radius: 120, color: '#3b82f6', label: 'Work'},\n"
    "       {type: 'circle', x: 400, y: 300, radius: 120, color: '#10b981', label: 'Life'},\n"
    "       {type: 'rect', x: 260, y: 300, width: 80, height: 80, color: 'rgba(0,0,0,0.1)', label: 'Balance'}\n"
    "     ]\n"
    "   }\n\n"

    "   🌐 NETWORK/CONNECTION CONCEPTS → Nodes with connecting lines\n"
    "   Keywords: network, connected, linked, relationship, web\n"
    "   SHAPES: Multiple circles as nodes, lines as connections\n"
    "   EXAMPLE: 'social network' → {\n"
    "     elements: [\n"
    "       {type: 'circle', x: 300, y: 300, radius: 40, color: '#6366f1', label: 'Me'},\n"
    "       {type: 'circle', x: 200, y: 200, radius: 30, color: '#8b5cf6', label: 'Friend 1'},\n"
    "       {type: 'circle', x: 400, y: 200, radius: 30, color: '#8b5cf6', label: 'Friend 2'},\n"
    "       {type: 'line', x: 300, y: 300, width: 100, height: -100},\n"
    "       {type: 'line', x: 300, y: 300, width: -100, height: -100}\n"
    "     ]\n"
    "   }\n\n"

    "   🌊 FLOW/PROCESS CONCEPTS → Arrows, curved lines, sequential shapes\n"
    "   Keywords: flow, process, stream, sequence, steps\n"
    "   SHAPES: Arrows, curved lines, sequential rectangles\n"
    "   EXAMPLE: 'data flow' → {\n"
    "     elements: [\n"
    "       {type: 'rect', x: 100, y: 300, width: 80, height: 60, color: '#3b82f6', label: 'Input'},\n"
    "       {type: 'arrow', x: 180, y: 330, width: 60, height: 0},\n"
    "       {type: 'rect', x: 240, y: 300, width: 120, height: 60, color: '#8b5cf6', label: 'Process'},\n"
    "       {type: 'arrow', x: 360, y: 330, width: 60, height: 0},\n"
    "       {type: 'rect', x: 420, y: 300, width: 80, height: 60, color: '#10b981', label: 'Output'}\n"
    "     ]\n"
    "   }\n\n"

    "   🎯 VENN DIAGRAMS → Overlapping circles for intersections\n"
    "   Keywords: overlap, intersection, common, shared, venn\n"
    "   SHAPES: Overlapping transparent circles\n"
    "   EXAMPLE: 'skills overlap' → {\n"
    "     elements: [\n"
    "       {type: 'circle', x: 250, y: 300, radius: 120, color: 'rgba(59,130,246,0.4)', label: 'Technical'},\n"
    "       {type: 'circle', x: 350, y: 300, radius: 120, color: 'rgba(236,72,153,0.4)', label: 'Creative'},\n"
    "       {type: 'text', x: 300, y: 300, label: 'Innovation'}\n"
    "     ]\n"
    "   }\n\n"

    "   📈 GROWTH/EXPANSION CONCEPTS → Increasing sizes, expanding shapes\n"
    "   Keywords: growth, expansion, evolution, progress, scaling\n"
    "   SHAPES: Progressively larger shapes, expanding circles\n"
    "   EXAMPLE: 'company growth' → {\n"
    "     elements: [\n"
    "       {type: 'circle', x: 150, y: 350, radius: 30, color: '#fbbf24', label: 'Startup'},\n"
    "       {type: 'circle', x: 250, y: 350, radius: 50, color: '#f59e0b', label: 'Growth'},\n"
    "       {type: 'circle', x: 380, y: 350, radius: 70, color: '#dc2626', label: 'Scale'},\n"
    "       {type: 'circle', x: 520, y: 350, radius: 90, color: '#991b1b', label: 'Enterprise'}\n"
    "     ]\n"
    "   }\n\n"

    "   🎯 TARGET/GOAL CONCEPTS → Concentric circles, bullseye patterns\n"
    "   Keywords: target, goal, objective, aim, focus, bullseye\n"
    "   SHAPES: Concentric circles with center focus\n"
    "   EXAMPLE: 'target market' → {\n"
    "     elements: [\n"
    "       {type: 'circle', x: 300, y: 300, radius: 200, color: 'rgba(239,68,68,0.2)', label: 'Total Market'},\n"
    "       {type: 'circle', x: 300, y: 300, radius: 140, color: 'rgba(251,146,60,0.3)', label: 'Addressable'},\n"
    "       {type: 'circle', x: 300, y: 300, radius: 80, color: 'rgba(250,204,21,0.4)', label: 'Serviceable'},\n"
    "       {type: 'circle', x: 300, y: 300, radius: 40, color: '#dc2626', label: 'Target'}\n"
    "     ]\n"
    "   }\n\n"

    "   🔀 TRANSFORMATION CONCEPTS → Before/after, input/output with transform arrow\n"
    "   Keywords: transform, change, convert, before/after, input/output\n"
    "   SHAPES: Shape → Arrow → Different shape\n"
    "   EXAMPLE: 'data transformation' → {\n"
    "     elements: [\n"
    "       {type: 'rect', x: 150, y: 300, width: 100, height: 80, color: '#94a3b8', label: 'Raw Data'},\n"
    "       {type: 'arrow', x: 250, y: 340, width: 100, height: 0},\n"
    "       {type: 'text', x: 300, y: 320, label: 'Transform'},\n"
    "       {type: 'circle', x: 450, y: 340, radius: 50, color: '#10b981', label: 'Insights'}\n"
    "     ]\n"
    "   }\n\n"

    "   🧩 COMPONENT/MODULAR CONCEPTS → Interlocking pieces, puzzle patterns\n"
    "   Keywords: component, module, piece, part, puzzle, building block\n"
    "   SHAPES: Interlocking rectangles or puzzle-piece shapes\n"
    "   EXAMPLE: 'system components' → {\n"
    "     elements: [\n"
    "       {type: 'rect', x: 200, y: 250, width: 100, height: 60, color: '#3b82f6', label: 'Frontend'},\n"
    "       {type: 'rect', x: 300, y: 250, width: 100, height: 60, color: '#8b5cf6', label: 'Backend'},\n"
    "       {type: 'rect', x: 250, y: 310, width: 100, height: 60, color: '#10b981', label: 'Database'},\n"
    "       {type: 'rect', x: 250, y: 190, width: 100, height: 60, color: '#f59e0b', label: 'API'}\n"
    "     ]\n"
    "   }\n\n"

    "   ⭐ RADIAL/STAR CONCEPTS → Central point with radiating elements\n"
    "   Keywords: radial, star, central, core, radiating, hub\n"
    "   SHAPES: Central circle with lines/shapes radiating outward\n"
    "   EXAMPLE: 'core values' → {\n"
    "     elements: [\n"
    "       {type: 'circle', x: 300, y: 300, radius: 50, color: '#6366f1', label: 'Core'},\n"
    "       {type: 'circle', x: 300, y: 200, radius: 30, color: '#8b5cf6', label: 'Innovation'},\n"
    "       {type: 'circle', x: 400, y: 250, radius: 30, color: '#8b5cf6', label: 'Quality'},\n"
    "       {type: 'circle', x: 400, y: 350, radius: 30, color: '#8b5cf6', label: 'Trust'},\n"
    "       {type: 'circle', x: 300, y: 400, radius: 30, color: '#8b5cf6', label: 'Service'},\n"
    "       {type: 'circle', x: 200, y: 350, radius: 30, color: '#8b5cf6', label: 'Team'},\n"
    "       {type: 'circle', x: 200, y: 250, radius: 30, color: '#8b5cf6', label: 'Ethics'}\n"
    "     ]\n"
    "   }\n\n"

    "   📊 MATRIX/GRID CONCEPTS → 2x2 matrices, quadrants, grids\n"
    "   Keywords: matrix, grid, quadrant, 2x2, four-box\n"
    "   SHAPES: Grid layout with labeled quadrants\n"
    "   EXAMPLE: 'urgency importance matrix' → {\n"
    "     elements: [\n"
    "       {type: 'rect', x: 150, y: 150, width: 150, height: 150, color: 'rgba(239,68,68,0.3)', label: 'Urgent Important'},\n"
    "       {type: 'rect', x: 300, y: 150, width: 150, height: 150, color: 'rgba(251,146,60,0.3)', label: 'Not Urgent Important'},\n"
    "       {type: 'rect', x: 150, y: 300, width: 150, height: 150, color: 'rgba(34,197,94,0.3)', label: 'Urgent Not Important'},\n"
    "       {type: 'rect', x: 300, y: 300, width: 150, height: 150, color: 'rgba(156,163,175,0.3)', label: 'Not Urgent Not Important'},\n"
    "       {type: 'text', x: 300, y: 100, label: 'Importance →'},\n"
    "       {type: 'text', x: 100, y: 300, label: 'Urgency ↓'}\n"
    "     ]\n"
    "   }\n\n"

    "⛔ WHEN NOT TO USE POLYLINES/SNAKEY DIAGRAMS:\n"
    "   - NEVER for cycles → Use circles/rings instead\n"
    "   - NEVER for hierarchies → Use triangles/pyramids/trees instead\n"
    "   - NEVER for balance/comparison → Use split shapes or side-by-side instead\n"
    "   - NEVER for networks → Use nodes with straight connections instead\n"
    "   - NEVER for growth → Use progressively larger shapes instead\n"
    "   - NEVER for grids/matrices → Use rectangles in grid layout instead\n\n"

    "✅ WHEN TO USE POLYLINES:\n"
    "   - ONLY for actual wavy/curved patterns (waves, rivers, snakes)\n"
    "   - ONLY for freeform artistic drawings\n"
    "   - ONLY when no conceptual pattern matches\n\n"

    "23. VECTORS & MATHEMATICAL OBJECTS:\n"
    "   USE FOR: vectors, vector spaces, mathematical objects, abstract algebra\n"
    "   KEYWORDS: vector, vector space, basis, span, linear algebra, abstract\n"
    "   CRITICAL: Always visualize vectors as arrows with coordinates labeled\n"
    "   EXAMPLE: 'show me one vector living on the vector space'\n"
    "   {{\n"
    "     \"visualType\": \"plotly\",\n"
    "     \"plotlySpec\": {{\n"
    "       \"data\": [\n"
    "         {{\n"
    "           \"type\": \"scatter\",\n"
    "           \"x\": [0, 3],\n"
    "           \"y\": [0, 4],\n"
    "           \"mode\": \"lines+markers+text\",\n"
    "           \"line\": {{\"color\": \"#3b82f6\", \"width\": 3}},\n"
    "           \"marker\": {{\"size\": 10, \"symbol\": \"arrow\", \"angleref\": \"previous\"}},\n"
    "           \"text\": [\"\", \"v = (3, 4)\"],\n"
    "           \"textposition\": \"top\",\n"
    "           \"name\": \"Vector v\"\n"
    "         }}\n"
    "       ],\n"
    "       \"layout\": {{\n"
    "         \"title\": \"Vector in R² Space\",\n"
    "         \"xaxis\": {{\"title\": \"x\", \"range\": [-1, 5], \"zeroline\": true}},\n"
    "         \"yaxis\": {{\"title\": \"y\", \"range\": [-1, 5], \"zeroline\": true}},\n"
    "         \"annotations\": [\n"
    "           {{\n"
    "             \"x\": 3, \"y\": 4,\n"
    "             \"ax\": 0, \"ay\": 0,\n"
    "             \"xref\": \"x\", \"yref\": \"y\",\n"
    "             \"axref\": \"x\", \"ayref\": \"y\",\n"
    "             \"text\": \"\",\n"
    "             \"showarrow\": true,\n"
    "             \"arrowhead\": 2,\n"
    "             \"arrowsize\": 1,\n"
    "             \"arrowwidth\": 3,\n"
    "             \"arrowcolor\": \"#3b82f6\"\n"
    "           }}\n"
    "         ]\n"
    "       }}\n"
    "     }}\n"
    "   }}\n\n"

    "OUTPUT FORMAT:\n"
    "{{\n"
    "  \"visualType\": \"plotly\",\n"
    "  \"plotlySpec\": {{\n"
    "    \"data\": [\n"
    "      {{\n"
    "        \"type\": \"scatter\",  // or 'bar', 'pie', 'sankey', 'sunburst', etc.\n"
    "        \"x\": [1, 2, 3, 4, 5],\n"
    "        \"y\": [10, 20, 25, 28, 29],\n"
    "        \"mode\": \"lines+markers\",\n"
    "        \"name\": \"Series Name\"\n"
    "      }}\n"
    "    ],\n"
    "    \"layout\": {{\n"
    "      \"title\": \"Chart Title\",\n"
    "      \"xaxis\": {{\"title\": \"X Axis\"}},\n"
    "      \"yaxis\": {{\"title\": \"Y Axis\"}}\n"
    "    }}\n"
    "  }}\n"
    "}}\n\n"

    "EXAMPLE 1: 'show diminishing returns'\n"
    "{{\n"
    "  \"visualType\": \"plotly\",\n"
    "  \"plotlySpec\": {{\n"
    "    \"data\": [\n"
    "      {{\n"
    "        \"type\": \"scatter\",\n"
    "        \"x\": [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10],\n"
    "        \"y\": [0, 5.0, 8.2, 10.4, 12.0, 13.2, 14.1, 14.8, 15.4, 15.8, 16.1],\n"
    "        \"mode\": \"lines+markers\",\n"
    "        \"name\": \"Returns\",\n"
    "        \"line\": {{\"color\": \"#3b82f6\", \"width\": 3}}\n"
    "      }}\n"
    "    ],\n"
    "    \"layout\": {{\n"
    "      \"title\": \"Diminishing Returns\",\n"
    "      \"xaxis\": {{\"title\": \"Input/Investment\"}},\n"
    "      \"yaxis\": {{\"title\": \"Output/Returns\"}}\n"
    "    }}\n"
    "  }}\n"
    "}}\n\n"

    "EXAMPLE 2: 'compare iPhone vs Samsung sales'\n"
    "{{\n"
    "  \"visualType\": \"plotly\",\n"
    "  \"plotlySpec\": {{\n"
    "    \"data\": [\n"
    "      {{\n"
    "        \"type\": \"bar\",\n"
    "        \"x\": [\"Q1\", \"Q2\", \"Q3\", \"Q4\"],\n"
    "        \"y\": [45, 52, 58, 61],\n"
    "        \"name\": \"iPhone\",\n"
    "        \"marker\": {{\"color\": \"#3b82f6\"}}\n"
    "      }},\n"
    "      {{\n"
    "        \"type\": \"bar\",\n"
    "        \"x\": [\"Q1\", \"Q2\", \"Q3\", \"Q4\"],\n"
    "        \"y\": [38, 42, 47, 51],\n"
    "        \"name\": \"Samsung\",\n"
    "        \"marker\": {{\"color\": \"#10b981\"}}\n"
    "      }}\n"
    "    ],\n"
    "    \"layout\": {{\n"
    "      \"title\": \"iPhone vs Samsung Quarterly Sales (millions)\",\n"
    "      \"barmode\": \"group\",\n"
    "      \"xaxis\": {{\"title\": \"Quarter\"}},\n"
    "      \"yaxis\": {{\"title\": \"Units Sold (M)\"}}\n"
    "    }}\n"
    "  }}\n"
    "}}\n\n"

    "EXAMPLE 3: 'exponential growth'\n"
    "{{\n"
    "  \"visualType\": \"plotly\",\n"
    "  \"plotlySpec\": {{\n"
    "    \"data\": [\n"
    "      {{\n"
    "        \"type\": \"scatter\",\n"
    "        \"x\": [0, 1, 2, 3, 4, 5, 6],\n"
    "        \"y\": [1, 2, 4, 8, 16, 32, 64],\n"
    "        \"mode\": \"lines+markers\",\n"
    "        \"name\": \"Exponential\",\n"
    "        \"line\": {{\"color\": \"#f59e0b\", \"width\": 3}}\n"
    "      }}\n"
    "    ],\n"
    "    \"layout\": {{\n"
    "      \"title\": \"Exponential Growth (2^x)\",\n"
    "      \"xaxis\": {{\"title\": \"Time\"}},\n"
    "      \"yaxis\": {{\"title\": \"Value\", \"type\": \"log\"}}\n"
    "    }}\n"
    "  }}\n"
    "}}\n\n"

    "EXAMPLE 4: 'market share pie chart'\n"
    "{{\n"
    "  \"visualType\": \"plotly\",\n"
    "  \"plotlySpec\": {{\n"
    "    \"data\": [\n"
    "      {{\n"
    "        \"type\": \"pie\",\n"
    "        \"labels\": [\"Chrome\", \"Safari\", \"Edge\", \"Firefox\", \"Other\"],\n"
    "        \"values\": [65, 19, 5, 4, 7],\n"
    "        \"marker\": {{\"colors\": [\"#3b82f6\", \"#10b981\", \"#f59e0b\", \"#ef4444\", \"#8b5cf6\"]}}\n"
    "      }}\n"
    "    ],\n"
    "    \"layout\": {{\n"
    "      \"title\": \"Browser Market Share 2024\"\n"
    "    }}\n"
    "  }}\n"
    "}}\n\n"

    "EXAMPLE 5: 'normal distribution'\n"
    "{{\n"
    "  \"visualType\": \"plotly\",\n"
    "  \"plotlySpec\": {{\n"
    "    \"data\": [\n"
    "      {{\n"
    "        \"type\": \"scatter\",\n"
    "        \"x\": [-4, -3.5, -3, -2.5, -2, -1.5, -1, -0.5, 0, 0.5, 1, 1.5, 2, 2.5, 3, 3.5, 4],\n"
    "        \"y\": [0.0001, 0.0009, 0.0044, 0.0175, 0.0540, 0.1295, 0.2420, 0.3521, 0.3989, 0.3521, 0.2420, 0.1295, 0.0540, 0.0175, 0.0044, 0.0009, 0.0001],\n"
    "        \"mode\": \"lines\",\n"
    "        \"fill\": \"tozeroy\",\n"
    "        \"name\": \"Normal Distribution\",\n"
    "        \"line\": {{\"color\": \"#3b82f6\"}}\n"
    "      }}\n"
    "    ],\n"
    "    \"layout\": {{\n"
    "      \"title\": \"Normal Distribution (Bell Curve)\",\n"
    "      \"xaxis\": {{\"title\": \"Standard Deviations\"}},\n"
    "      \"yaxis\": {{\"title\": \"Probability Density\"}}\n"
    "    }}\n"
    "  }}\n"
    "}}\n\n"

    "EXAMPLE 6: 'plot sigmoid function' or 'plot σ(x) = 1/(1+e^-x)'\n"
    "{{\n"
    "  \"visualType\": \"plotly\",\n"
    "  \"plotlySpec\": {{\n"
    "    \"data\": [\n"
    "      {{\n"
    "        \"type\": \"scatter\",\n"
    "        \"x\": [-10, -9, -8, -7, -6, -5, -4, -3, -2, -1, 0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10],\n"
    "        \"y\": [0.00005, 0.00012, 0.0003, 0.0009, 0.0025, 0.0067, 0.0180, 0.0474, 0.119, 0.269, 0.5, 0.731, 0.881, 0.953, 0.982, 0.993, 0.998, 0.999, 0.9997, 0.9999, 0.99995],\n"
    "        \"mode\": \"lines\",\n"
    "        \"name\": \"Sigmoid(x)\",\n"
    "        \"line\": {{\"color\": \"#3b82f6\", \"width\": 3}}\n"
    "      }}\n"
    "    ],\n"
    "    \"layout\": {{\n"
    "      \"title\": \"Sigmoid Activation Function\",\n"
    "      \"xaxis\": {{\"title\": \"x\", \"zeroline\": true}},\n"
    "      \"yaxis\": {{\"title\": \"σ(x)\", \"range\": [0, 1]}},\n"
    "      \"annotations\": [\n"
    "        {\n"
    "          \"text\": \"$\\\\sigma(x) = \\\\frac{1}{1 + e^{-x}}$\",\n"
    "          \"x\": 0.5,\n"
    "          \"y\": 1.15,\n"
    "          \"xref\": \"paper\",\n"
    "          \"yref\": \"paper\",\n"
    "          \"showarrow\": false,\n"
    "          \"font\": {\"size\": 20}\n"
    "        }\n"
    "      ]\n"
    "    }}\n"
    "  }}\n"
    "}}\n\n"

    "EXAMPLE 7: 'plot E=mc²' or 'plot energy mass relationship'\n"
    "{{\n"
    "  \"visualType\": \"plotly\",\n"
    "  \"plotlySpec\": {{\n"
    "    \"data\": [\n"
    "      {{\n"
    "        \"type\": \"scatter\",\n"
    "        \"x\": [0, 0.5, 1, 1.5, 2, 2.5, 3, 3.5, 4, 4.5, 5],\n"
    "        \"y\": [0, 4.5e16, 9e16, 1.35e17, 1.8e17, 2.25e17, 2.7e17, 3.15e17, 3.6e17, 4.05e17, 4.5e17],\n"
    "        \"mode\": \"lines+markers\",\n"
    "        \"name\": \"E = mc²\",\n"
    "        \"line\": {{\"color\": \"#ef4444\", \"width\": 3}}\n"
    "      }}\n"
    "    ],\n"
    "    \"layout\": {{\n"
    "      \"title\": \"Mass-Energy Equivalence\",\n"
    "      \"xaxis\": {{\"title\": \"Mass (kg)\"}},\n"
    "      \"yaxis\": {{\"title\": \"Energy (Joules)\"}},\n"
    "      \"annotations\": [\n"
    "        {\n"
    "          \"text\": \"$E = mc^2$ where $c = 3 \\\\times 10^8$ m/s\",\n"
    "          \"x\": 0.5,\n"
    "          \"y\": 1.15,\n"
    "          \"xref\": \"paper\",\n"
    "          \"yref\": \"paper\",\n"
    "          \"showarrow\": false,\n"
    "          \"font\": {\"size\": 18}\n"
    "        }\n"
    "      ]\n"
    "    }}\n"
    "  }}\n"
    "}}\n\n"

    "FALLBACK FOR RELATIONSHIPS (use Sankey for flow/hierarchy):\n"
    "EXAMPLE 8: 'compare ML and DL'\n"
    "{{\n"
    "  \"visualType\": \"plotly\",\n"
    "  \"plotlySpec\": {{\n"
    "    \"data\": [\n"
    "      {{\n"
    "        \"type\": \"sankey\",\n"
    "        \"node\": {{\n"
    "          \"label\": [\"AI\", \"Machine Learning\", \"Deep Learning\", \"Supervised\", \"Unsupervised\", \"CNN\", \"RNN\", \"Transformer\"],\n"
    "          \"color\": [\"#3b82f6\", \"#10b981\", \"#f59e0b\", \"#ef4444\", \"#8b5cf6\", \"#ec4899\", \"#06b6d4\", \"#84cc16\"]\n"
    "        }},\n"
    "        \"link\": {{\n"
    "          \"source\": [0, 1, 1, 2, 2, 2],\n"
    "          \"target\": [1, 2, 3, 5, 6, 7],\n"
    "          \"value\": [10, 8, 5, 3, 3, 2]\n"
    "        }}\n"
    "      }}\n"
    "    ],\n"
    "    \"layout\": {{\"title\": \"AI → ML → DL Hierarchy\"}}\n"
    "  }}\n"
    "}}\n\n"

    "---\n\n"

    "User request: \"{prompt}\"\n\n"
    "Return ONLY valid JSON:\n"
    "{{\n"
    "  \"visualType\": \"conceptual\" | \"mathematical_interactive\" | \"mathematical\" | \"timeline\" | \"statistical\",\n"
    "  \"expression\": \"...\"     // For single function (mathematical_interactive or mathematical)\n"
    "  \"expressions\": [\"...\"]   // For multiple functions (mathematical_interactive)\n"
    "  \"elements\": [...]         // For element-based visuals\n"
    "  \"nodes\": [...]            // For network/relationship graphs (use with links)\n"
    "  \"links\": [...]            // For connections between nodes\n"
    "}}\n\n"
    "IMPORTANT: For mathematical expressions:\n"
    "- Use Python syntax: x**2 (not x²), 3*x (not 3x), sqrt(x) (not √x)\n"
    "- Expression must be in terms of x: \"x**2 - 4*x + 3\" (not \"y = x**2 - 4*x + 3\")\n"
    "- Use explicit operators: * for multiply, ** for power, / for divide\n"
    "- Common functions: sin(x), cos(x), tan(x), exp(x), log(x), sqrt(x), abs(x)\n"
    "- For equations like y=mx+b, convert to expression: \"m*x + b\" and define parameters m,b\n\n"
    "For RELATIONSHIP/NETWORK queries (\"relationship between\", \"connection\", \"compare\"), use nodes/links:\n"
    "{{\n"
    "  \"visualType\": \"conceptual\",\n"
    "  \"nodes\": [{{\"id\": \"ai\", \"label\": \"Artificial Intelligence\", \"color\": \"#3b82f6\"}}],\n"
    "  \"links\": [{{\"source\": \"ai\", \"target\": \"ml\", \"label\": \"includes\"}}],\n"
    "  \"elements\": [{{\"type\": \"node\"}}]  // Add at least one node element for detection\n"
    "}}\n\n"
    "Be precise and educational."
)


def call_openai_for_spec(command: str, user_context: str = None, tier_model: str = None, use_local_llm: bool = None, local_llm_model: str = None, routing_hint: str = None) -> Dict[str, Any]:
    """
    Call OpenAI API or local LLM to generate visualization spec.

    Args:
        command: User's visualization command
        user_context: Optional context about what user is working on
        tier_model: Model to use based on user's subscription tier (e.g., "gpt-4o-mini" for free, "gpt-4o" for pro)
        use_local_llm: Whether to use local LLM (Ollama) instead of OpenAI (tier-based, overrides global USE_LOCAL_LLM)
        local_llm_model: Local LLM model name (tier-based, overrides global LOCAL_LLM_MODEL)
        routing_hint: Suggested visualization type based on query analysis (e.g., "comparison", "workflow", "hierarchy")
    """
    # Determine whether to use local LLM: tier config > global env variable
    should_use_local = use_local_llm if use_local_llm is not None else USE_LOCAL_LLM

    # Support local LLM (Ollama) or OpenAI
    if should_use_local:
        # Use Ollama with OpenAI-compatible API
        http_client = httpx.Client()
        client = OpenAI(
            base_url=LOCAL_LLM_BASE_URL,
            api_key="ollama",  # Ollama doesn't need a real key
            http_client=http_client
        )
        # Use tier-specific local model if provided, otherwise fallback to global env variable
        model_to_use = local_llm_model if local_llm_model else LOCAL_LLM_MODEL
        print(f"[LLM] Using LOCAL LLM via Ollama: {model_to_use}")
    else:
        # Use OpenAI
        if not OPENAI_API_KEY:
            raise RuntimeError("Missing OPENAI_API_KEY")
        http_client = httpx.Client()
        client_kwargs = {"api_key": OPENAI_API_KEY, "http_client": http_client}
        if OPENAI_ORG:
            client_kwargs["organization"] = OPENAI_ORG
        if OPENAI_PROJECT:
            client_kwargs["project"] = OPENAI_PROJECT
        client = OpenAI(**client_kwargs)
        # Use tier-specific model if provided, otherwise fallback to env variable
        model_to_use = tier_model if tier_model else MODEL
        print(f"[LLM] Using OpenAI: {model_to_use}")

    # Build prompt with optional user context and routing hints
    prompt = PROMPT_TEMPLATE.replace("{prompt}", command)

    # Add routing hint to guide AI towards the right visualization type
    if routing_hint:
        hint_guidance = {
            "comparison": "\n🎯 ROUTING HINT: This is a COMPARISON query. Use Plotly bar chart or pie chart with actual data.\n",
            "workflow": "\n🎯 ROUTING HINT: This is a WORKFLOW/PROCESS query. Use Sankey diagram (type: 'sankey') with flowing connections.\n",
            "hierarchy": "\n🎯 ROUTING HINT: This is a HIERARCHY query. Use Sunburst or Treemap visualization.\n",
            "timeseries": "\n🎯 ROUTING HINT: This is a TIME SERIES query. Use line or area chart showing change over time.\n",
            "network": "\n🎯 ROUTING HINT: This is a NETWORK/RELATIONSHIP query. Use nodes and links for D3 graph.\n"
        }
        if routing_hint in hint_guidance:
            prompt = hint_guidance[routing_hint] + prompt

    # If user has provided context about what they're working on, add it to help AI generate more relevant visualizations
    # CRITICAL: Context should modify HOW we visualize, NOT WHAT we visualize
    if user_context and user_context.strip():
        context_prefix = (
            f"\n\n📋 USER'S BACKGROUND CONTEXT: The user is working on: {user_context.strip()}\n\n"
            f"⚠️ CRITICAL INSTRUCTION: This context describes the user's general work area, but you MUST visualize what they ACTUALLY REQUESTED.\n"
            f"- If they request 'machine learning pipeline', show ML pipeline (NOT the context topic)\n"
            f"- If they request 'compare iPhone vs Android', show that comparison (NOT the context topic)\n"
            f"- Use the context ONLY to adjust complexity, terminology, or style (e.g., simpler for students, technical for professionals)\n"
            f"- NEVER change the core subject of the visualization based on context\n\n"
        )
        prompt = context_prefix + prompt

    # o3-mini, o1 series, and gpt-5 models don't support temperature/response_format
    api_params = {
        "model": model_to_use,
        "messages": [{"role": "user", "content": prompt}],
    }

    # Only add these params for models that support them
    if not model_to_use.startswith("o1") and not model_to_use.startswith("o3") and not model_to_use.startswith("gpt-5"):
        api_params["temperature"] = 0
        api_params["response_format"] = {"type": "json_object"}

    res = client.chat.completions.create(**api_params)
    content = res.choices[0].message.content
    result = json.loads(content)
    # Log for debugging
    print(f"[LLM DEBUG] Raw output: {json.dumps(result, indent=2)}")
    print(f"[LLM DEBUG] Has nodes: {'nodes' in result}")
    print(f"[LLM DEBUG] Has links: {'links' in result}")
    print(f"[LLM DEBUG] Has elements: {'elements' in result}")
    return result


def llm_ready() -> bool:
    return USE_LOCAL_LLM or bool(OPENAI_API_KEY)


def fallback_naive(command: str) -> Dict[str, Any]:
    text = command.lower()
    color = next((c for c in ["red","blue","green","yellow","purple","orange","black","white"] if c in text), "#1e90ff")
    if "circle" in text:
        spec = {"elements": [{"type": "circle", "x": 200, "y": 200, "radius": 60, "color": color}]}
    elif any(k in text for k in ["rectangle","rect","box","square"]):
        spec = {"elements": [{"type": "rect", "x": 150, "y": 150, "width": 160, "height": 100, "color": color}]}
        if "square" in text:
            spec["elements"][0]["height"] = spec["elements"][0]["width"]
    elif any(k in text for k in ["triangle","pyramid"]):
        spec = {"elements": [{"type": "triangle", "x": 180, "y": 160, "width": 140, "height": 120, "color": color}]}
    elif any(k in text for k in ["ellipse","oval"]):
        spec = {"elements": [{"type": "ellipse", "x": 180, "y": 160, "width": 180, "height": 120, "color": color}]}
    elif "line" in text:
        spec = {"elements": [{"type": "line", "x": 100, "y": 100, "width": 220, "height": 0, "color": color}]}
    else:
        # Default: create a labeled card for the subject instead of echoing the full prompt
        subject = extract_subject(command) or "Item"
        spec = {"elements": _build_label_card(subject)}
    return spec


def _coerce_int(v, default=None):
    try:
        if v is None:
            return default
        return int(round(float(v)))
    except Exception:
        return default


def normalize_spec(spec: Dict[str, Any]) -> Dict[str, Any]:
    elements = spec.get("elements") or []
    visual_type = spec.get("visualType", "conceptual")  # Preserve visualType
    normed = []
    logging.getLogger("llm").info(f"Normalizing {len(elements)} elements for {visual_type} visualization")

    # For plotly, pass through with plotlySpec
    if visual_type == "plotly":
        if "plotlySpec" in spec:
            return {"visualType": visual_type, "plotlySpec": spec["plotlySpec"]}
        else:
            logging.getLogger("llm").error("plotly visualType but no plotlySpec found!")
            return {"visualType": "conceptual", "elements": []}

    # For mermaid, pass through with mermaidCode
    if visual_type == "mermaid":
        if "mermaidCode" in spec:
            return {"visualType": visual_type, "mermaidCode": spec["mermaidCode"]}
        else:
            logging.getLogger("llm").error("mermaid visualType but no mermaidCode found!")
            return {"visualType": "conceptual", "elements": []}

    # For mathematical_interactive, pass through with expression or expressions
    if visual_type == "mathematical_interactive":
        # Handle both single expression and multiple expressions
        if "expressions" in spec and isinstance(spec["expressions"], list):
            return {"visualType": visual_type, "expressions": spec["expressions"]}
        else:
            expression = spec.get("expression", "")
            return {"visualType": visual_type, "expression": expression}

    # For mathematical visualizations, pass through with expression
    if visual_type == "mathematical":
        # Mathematical type should have expression or expressions, not elements
        if "expressions" in spec and isinstance(spec["expressions"], list):
            return {"visualType": visual_type, "expressions": spec["expressions"]}
        elif "expression" in spec:
            return {"visualType": visual_type, "expression": spec["expression"]}
        else:
            # Fallback: if no expression provided, log error and treat as conceptual
            logging.getLogger("llm").error("mathematical visualType but no expression found!")
            return {"visualType": "conceptual", "elements": elements}

    # For conceptual/timeline/statistical, apply existing normalization
    for e in elements:
        t = str(e.get("type", "")).strip().lower()
        # Type synonyms
        if t in {"rectangle", "box"}:
            t = "rect"
        if t in {"square"}:
            t = "rect"
            size = e.get("size") or e.get("width") or e.get("height") or 100
            e["width"], e["height"] = size, size
        if t in {"pyramid"}:
            t = "triangle"
        if t in {"oval"}:
            t = "ellipse"
        if t in {"arrow"}:
            t = "line"

        x = _coerce_int(e.get("x"), 100)
        y = _coerce_int(e.get("y"), 100)
        color = e.get("color") or e.get("fill") or e.get("backgroundColor") or "#1e90ff"

        # Property normalization
        radius = _coerce_int(e.get("radius") or e.get("r") or e.get("size"))
        width = _coerce_int(e.get("width") or e.get("w"))
        height = _coerce_int(e.get("height") or e.get("h"))

        if t == "circle":
            radius = radius or 60
        elif t in {"rect", "triangle", "ellipse", "line"}:
            width = width or (180 if t != "line" else 220)
            height = height or (120 if t != "line" else 0)

        label = e.get("label") or e.get("text")

        points = None
        if isinstance(e.get("points"), list):
            pts = []
            for p in e.get("points"):
                try:
                    px = _coerce_int(p.get("x"))
                    py = _coerce_int(p.get("y"))
                    if px is not None and py is not None:
                        pts.append({"x": px, "y": py})
                except Exception:
                    continue
            points = pts or None

        # Handle connector points
        from_point = None
        to_point = None
        if t == "connector":
            print(f"[CONNECTOR DEBUG] Processing: {e}")
            if isinstance(e.get("from_point"), dict):
                from_point = {
                    "x": _coerce_int(e["from_point"].get("x"), 0),
                    "y": _coerce_int(e["from_point"].get("y"), 0)
                }
            if isinstance(e.get("to_point"), dict):
                to_point = {
                    "x": _coerce_int(e["to_point"].get("x"), 0),
                    "y": _coerce_int(e["to_point"].get("y"), 0)
                }
            print(f"[CONNECTOR DEBUG] Processed - from: {from_point}, to: {to_point}")

        # Extract src for image elements
        src = e.get("src") if t == "image" else None

        # Handle celebrity images - fetch from Wikipedia if celebrity_name is provided
        if t == "image" and not src and e.get("celebrity_name"):
            celebrity_name = e.get("celebrity_name")
            logging.getLogger("llm").info(f"Fetching Wikipedia image for: {celebrity_name}")
            wikipedia_url = fetch_wikipedia_image_sync(celebrity_name)
            if wikipedia_url:
                src = wikipedia_url
                logging.getLogger("llm").info(f"Found Wikipedia image: {src}")
            else:
                logging.getLogger("llm").warning(f"No Wikipedia image found for: {celebrity_name}")

        # Handle anatomy images - fetch from Wikipedia if anatomy_term is provided
        if t == "image" and not src and e.get("anatomy_term"):
            anatomy_term = e.get("anatomy_term")
            logging.getLogger("llm").info(f"Fetching Wikipedia anatomy image for: {anatomy_term}")
            wikipedia_url = fetch_wikipedia_image_sync(anatomy_term)
            if wikipedia_url:
                src = wikipedia_url
                logging.getLogger("llm").info(f"Found Wikipedia anatomy image: {src}")
            else:
                logging.getLogger("llm").warning(f"No Wikipedia anatomy image found for: {anatomy_term}")

        # Handle geography images - fetch from Wikipedia if geography_term is provided
        if t == "image" and not src and e.get("geography_term"):
            geography_term = e.get("geography_term")
            logging.getLogger("llm").info(f"Fetching Wikipedia geography image for: {geography_term}")
            wikipedia_url = fetch_wikipedia_image_sync(geography_term)
            if wikipedia_url:
                src = wikipedia_url
                logging.getLogger("llm").info(f"Found Wikipedia geography image: {src}")
            else:
                logging.getLogger("llm").warning(f"No Wikipedia geography image found for: {geography_term}")

        # Extract text-specific properties
        fontSize = e.get("fontSize")
        fontWeight = e.get("fontWeight")
        textAlign = e.get("textAlign")

        normed.append(
            {
                "type": t or "text",
                "x": x,
                "y": y,
                **({"radius": radius} if radius is not None else {}),
                **({"width": width} if width is not None else {}),
                **({"height": height} if height is not None else {}),
                **({"label": label} if label else {}),
                **({"points": points} if points else {}),
                **({"from_point": from_point} if from_point else {}),
                **({"to_point": to_point} if to_point else {}),
                **({"src": src} if src else {}),
                **({"fontSize": fontSize} if fontSize else {}),
                **({"fontWeight": fontWeight} if fontWeight else {}),
                **({"textAlign": textAlign} if textAlign else {}),
                "color": color,
            }
        )
    return {"visualType": visual_type, "elements": normed}


def extract_subject(command: str) -> str:
    s = (command or "").strip()
    lower = s.lower()
    prefixes = [
        "show me ", "show ", "draw ", "visualize ", "render ", "make ", "create ",
    ]
    for p in prefixes:
        if lower.startswith(p):
            s = s[len(p):]
            break
    # Trim common articles/punctuation
    s = s.strip().lstrip("a ").lstrip("an ").lstrip("the ").strip().strip(".?!")
    # Title-case short subject
    return s[:64].title() if s else ""


def _build_label_card(subject: str) -> List[Dict[str, Any]]:
    # Simple card: background rect + centered-ish label
    x, y = 140, 120
    w, h = 280, 140
    bg = {"type": "rect", "x": x, "y": y, "width": w, "height": h, "color": "#e0e7ff"}
    txt = {"type": "text", "x": x + 16, "y": y + 16, "label": subject, "color": "#111827"}
    return [bg, txt]


def interpret_command(command: str) -> Dict[str, Any]:
    # 1) Deterministic rules for known patterns (math plots, flowcharts)
    rule_spec = interpret_by_rules(command)
    if rule_spec:
        return rule_spec

    # 2) LLM-based interpretation
    try:
        raw = call_openai_for_spec(command)
    except Exception:
        logging.getLogger("llm").warning("LLM call failed; using fallback", exc_info=True)
        raw = fallback_naive(command)
    norm = normalize_spec(raw)

    # 3) If still only text or empty, fall back to labeled card
    # BUT: preserve intentional long-form text messages from LLM (like error messages)
    elements = norm.get("elements") or []
    if not elements:
        subject = extract_subject(command) or "Item"
        return {"elements": _build_label_card(subject)}

    # If all elements are text, check if it's an intentional message (long text)
    if all((e.get("type") == "text") for e in elements):
        first_label = elements[0].get("label") or elements[0].get("text") or ""
        # If the text is long (>50 chars), it's likely an intentional message - preserve it
        if len(first_label) > 50:
            return norm
        # Otherwise, replace with a simple card
        subject = extract_subject(command) or first_label
        return {"elements": _build_label_card(subject)}
    return norm


def interpret_with_source(command: str, user_context: str = None, subscription_tier: str = "FREE"):
    """Return (spec, source, error) where source is one of image|llm|rules|fallback|error.
    If AI_REQUIRE is true and no AI path succeeds, returns (None, 'error', message).

    Args:
        command: The user's visualization command
        user_context: Optional context about what the user is working on (e.g., "preparing presentation for executives")
        subscription_tier: User's subscription tier (FREE, PRO, TEAM, ENTERPRISE) - determines which model to use
    """
    from .config import get_tier_config

    # Get tier-specific configuration
    tier_config = get_tier_config(subscription_tier)
    tier_model = tier_config["llm_model"]
    enable_images = tier_config["enable_images"]
    use_local_llm = tier_config.get("use_local_llm", False)
    local_llm_model = tier_config.get("local_llm_model")

    print(f"[TIER CONFIG] Tier: {subscription_tier}, Model: {tier_model}, Local LLM: {use_local_llm}, Local Model: {local_llm_model}, Images: {enable_images}")

    print(f"[INTERPRET_WITH_SOURCE] Starting with command: {command[:100]}")
    print(f"[INTERPRET_WITH_SOURCE] User context: {user_context}")
    last_error = None

    # OPTIMIZATION: Check if this looks like a mathematical query first (fast rule-based check)
    cmd_lower = command.lower()
    print(f"[INTERPRET_WITH_SOURCE] cmd_lower: {cmd_lower[:100]}")
    math_keywords = ["plot", "graph", "parabola", "function", "equation", "y=", "x=", "tangent", "derivative", "sin", "cos", "tan", "integral"]
    is_math = any(kw in cmd_lower for kw in math_keywords)

    # For math queries, try rules first (instant, no API call)
    if is_math and not AI_DISABLE_RULES:
        rule_spec = interpret_by_rules(command)
        if rule_spec:
            return rule_spec, "rules", None

    # SMART ROUTING: Choose best visualization type based on query intent

    # Data comparison patterns → Force Plotly bar/pie charts
    comparison_keywords = ["compare", "vs", "versus", "which is better", "difference between", "comparison"]
    is_comparison = any(kw in cmd_lower for kw in comparison_keywords)

    # Workflow/process patterns → Force Mermaid sequence diagrams OR Sankey
    workflow_keywords = ["workflow", "pipeline", "process", "lifecycle", "how does", "how do", "steps", "stages", "procedure", "sequence"]
    is_workflow = any(kw in cmd_lower for kw in workflow_keywords)

    # Hierarchy patterns → Force Sunburst/Treemap
    hierarchy_keywords = ["hierarchy", "organization", "org chart", "structure", "tree", "taxonomy"]
    is_hierarchy = any(kw in cmd_lower for kw in hierarchy_keywords)

    # Relationship/network patterns → D3 network graph
    network_keywords = ["network", "connection", "relationship", "relate", "between", "connect"]
    is_network = any(kw in cmd_lower for kw in network_keywords) and not is_comparison

    # Time series patterns → Force line/area charts
    timeseries_keywords = ["over time", "growth", "trend", "forecast", "historical", "change over"]
    is_timeseries = any(kw in cmd_lower for kw in timeseries_keywords)

    # Mermaid-specific patterns (for sequential processes like auth flows)
    mermaid_keywords = ["authentication", "oauth", "login", "api request", "http", "sequence"]
    use_mermaid = is_workflow and any(kw in cmd_lower for kw in mermaid_keywords)

    print(f"[ROUTING] comparison={is_comparison}, workflow={is_workflow}, hierarchy={is_hierarchy}, network={is_network}, timeseries={is_timeseries}, mermaid={use_mermaid}, math={is_math}")

    # Route to Mermaid for sequential processes (OAuth, login flows, etc.)
    if not is_math and use_mermaid:
        print("[ROUTING] Detected sequential process - using Mermaid sequence diagram")
        mermaid_spec = try_generate_mermaid_diagram(command)
        if mermaid_spec:
            return mermaid_spec, "mermaid", None
        print("[ROUTING] Mermaid failed, falling back to LLM for Sankey")

    # Route to D3 network graph for relationships (but not comparisons)
    if not is_math and is_network:
        print("[ROUTING] Detected network/relationship - using D3 graph with nodes/links")
        # Fall through to LLM which will generate nodes/links structure

    # Check if this needs AI image generation (NOT for logos - those use clearbit URLs)
    # Only generate images for: illustrations, drawings, realistic scenes, diagrams
    generate_image_keywords = ["illustration", "drawing", "realistic", "diagram", "scene", "picture"]
    needs_ai_image = any(kw in cmd_lower for kw in generate_image_keywords)

    # Skip image generation for logos/brands - LLM will use clearbit URLs instead
    is_logo_request = any(kw in cmd_lower for kw in ["logo", "brand"])

    # Try AI image generation for complex graphics (NOT logos)
    # Only for PRO+ tiers
    if enable_images and (needs_ai_image or AI_IMAGE_FIRST) and not is_logo_request:
        print(f"[ROUTING] AI image generation requested (needs_ai_image={needs_ai_image}, AI_IMAGE_FIRST={AI_IMAGE_FIRST})")
        img_spec = try_generate_image_spec(command)
        if img_spec:
            return img_spec, "image", None
        print("[ROUTING] AI image generation failed or unavailable, falling back to LLM")
    elif not enable_images and (needs_ai_image or AI_IMAGE_FIRST) and not is_logo_request:
        print(f"[ROUTING] AI image generation disabled for {subscription_tier} tier - upgrade to PRO for image generation")

    # Determine routing hint to guide AI
    routing_hint = None
    if is_comparison:
        routing_hint = "comparison"
    elif is_workflow:
        routing_hint = "workflow"
    elif is_hierarchy:
        routing_hint = "hierarchy"
    elif is_timeseries:
        routing_hint = "timeseries"
    elif is_network:
        routing_hint = "network"

    # Step 1: Try LLM classification with smart routing hint
    try:
        raw = call_openai_for_spec(command, user_context=user_context, tier_model=tier_model, use_local_llm=use_local_llm, local_llm_model=local_llm_model, routing_hint=routing_hint)

        # Check if LLM returned nodes/links (for D3 graphs) - if so, return RAW without normalizing
        # Allow empty links array for single-node visualizations (logos, single items)
        if raw.get("nodes"):
            print(f"[INTERPRET] LLM returned nodes structure - returning raw spec")
            return raw, "llm", None

        # Otherwise normalize for element-based rendering
        norm = normalize_spec(raw)
        visual_type = norm.get("visualType", "conceptual")

        # For plotly, return with plotlySpec
        if visual_type == "plotly":
            if norm.get("plotlySpec"):
                return norm, "llm", None
            # If visualType is plotly but no spec, log error but continue to fallback
            print(f"[LLM ERROR] visualType='plotly' but no plotlySpec provided")
            last_error = "LLM returned plotly type without plotlySpec"

        # For mermaid, return with mermaidCode
        elif visual_type == "mermaid":
            if norm.get("mermaidCode"):
                return norm, "llm", None
            # If visualType is mermaid but no code, log error but continue to fallback
            print(f"[LLM ERROR] visualType='mermaid' but no mermaidCode provided")
            last_error = "LLM returned mermaid type without mermaidCode"

        # For mathematical or mathematical_interactive, use our engine
        elif visual_type in ["mathematical", "mathematical_interactive"]:
            if norm.get("expression") or norm.get("expressions"):
                return norm, "llm", None
            # If visualType is mathematical but no expression, log error but continue to fallback
            print(f"[LLM ERROR] visualType='{visual_type}' but no expression provided")
            last_error = f"LLM returned {visual_type} type without expression"

        # For element-based types (conceptual, timeline, statistical, etc)
        else:
            elements = norm.get("elements") or []
            if elements and len(elements) > 0:
                # Accept any elements that aren't empty
                return norm, "llm", None
            # If visualType set but no elements, log error
            if visual_type != "conceptual":
                print(f"[LLM ERROR] visualType='{visual_type}' but no elements provided")
            last_error = "LLM returned no valid visualization data"
    except Exception as e:
        last_error = str(e)
        logging.getLogger("llm").warning("LLM call failed", exc_info=True)

    # Rules (optional)
    if not AI_DISABLE_RULES:
        rule_spec = interpret_by_rules(command)
        if rule_spec:
            return rule_spec, "rules", None

    # Fallback or error
    if AI_REQUIRE:
        return None, "error", last_error or "AI unavailable"
    return fallback_naive(command), "fallback", last_error
