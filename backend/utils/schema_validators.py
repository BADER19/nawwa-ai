from datetime import datetime
from typing import List, Optional, Any
from pydantic import BaseModel, EmailStr, Field, field_validator
import re


class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"


class UserCreate(BaseModel):
    email: EmailStr
    username: str = Field(min_length=2, max_length=100)
    password: str = Field(min_length=8)

    @field_validator('password')
    @classmethod
    def validate_password_complexity(cls, v: str) -> str:
        """
        Enforce strong password policy:
        - At least 8 characters
        - At least one uppercase letter
        - At least one lowercase letter
        - At least one number
        - At least one special character
        """
        if len(v) < 8:
            raise ValueError('Password must be at least 8 characters long')

        if not re.search(r'[A-Z]', v):
            raise ValueError('Password must contain at least one uppercase letter')

        if not re.search(r'[a-z]', v):
            raise ValueError('Password must contain at least one lowercase letter')

        if not re.search(r'\d', v):
            raise ValueError('Password must contain at least one number')

        if not re.search(r'[!@#$%^&*(),.?":{}|<>_\-+=\[\]\\\/`~]', v):
            raise ValueError('Password must contain at least one special character (!@#$%^&*(),.?":{}|<>_-+=[]\\\/`~)')

        return v


class UserOut(BaseModel):
    id: int
    email: EmailStr
    username: str
    current_context: Optional[str] = None
    created_at: datetime

    class Config:
        from_attributes = True


class UserContextUpdate(BaseModel):
    current_context: str = Field(default="", max_length=500, min_length=0)  # Allow empty string to clear context


class VisualizeRequest(BaseModel):
    command: str = Field(..., example="draw a red circle")
    user_context: Optional[str] = None  # What user is working on today


class ElementSpec(BaseModel):
    type: str  # Basic: circle, rect, line, text, triangle, ellipse, polygon, polyline, arrow, image
               # Advanced: connector, textbox, group, node, function, axes, point, annotation
    x: Optional[float] = 100  # Allow floats for mathematical coordinates
    y: Optional[float] = 100
    radius: Optional[float] = None
    width: Optional[float] = None
    height: Optional[float] = None
    color: Optional[str] = None

    # Mathematical visualization fields
    expression: Optional[str] = None  # For function type
    domain: Optional[List[float]] = None  # [min, max] for function domain
    xRange: Optional[List[float]] = None  # For axes
    yRange: Optional[List[float]] = None  # For axes
    xLabel: Optional[str] = None
    yLabel: Optional[str] = None
    anchor: Optional[str] = None  # For annotations

    # Text and labels
    label: Optional[str] = None
    text: Optional[str] = None  # Multi-line text for textboxes
    fontSize: Optional[int] = None
    fontWeight: Optional[str] = None
    textAlign: Optional[str] = None

    # Shapes and paths
    points: Optional[List[dict]] = None  # list of {x:int, y:int}
    src: Optional[str] = None  # for images (data URL or remote URL)

    # Connectors (arrows between elements)
    from_id: Optional[str] = None  # ID of source element
    to_id: Optional[str] = None    # ID of target element
    from_point: Optional[dict] = None  # {x, y} for direct coordinates
    to_point: Optional[dict] = None    # {x, y} for direct coordinates

    # Grouping and hierarchy
    id: Optional[str] = None       # Unique identifier for referencing
    group_id: Optional[str] = None  # ID of parent group
    children: Optional[List[str]] = None  # IDs of child elements

    # Styling
    borderColor: Optional[str] = None
    borderWidth: Optional[int] = None
    backgroundColor: Optional[str] = None
    opacity: Optional[float] = None


class VisualSpec(BaseModel):
    visualType: Optional[str] = "conceptual"  # conceptual, mathematical, mathematical_interactive, timeline, statistical, mermaid, plotly
    elements: Optional[List[ElementSpec]] = None  # Required for most types, but not for mathematical_interactive or mermaid
    expression: Optional[str] = None  # For mathematical_interactive type (single function)
    expressions: Optional[List[str]] = None  # For mathematical_interactive type (multiple functions)
    mermaidCode: Optional[str] = None  # For mermaid type diagrams
    nodes: Optional[List[dict]] = None  # For D3 network graphs (nodes)
    links: Optional[List[dict]] = None  # For D3 network graphs (links between nodes)
    plotlySpec: Optional[dict] = None  # For plotly universal charts (complete Plotly.js specification)


class WorkspaceCreate(BaseModel):
    name: str
    data: VisualSpec


class WorkspaceOut(BaseModel):
    id: int
    name: str
    data: Any
    owner_id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class AuthLogin(BaseModel):
    email: EmailStr
    password: str


# Project schemas
class ProjectCreate(BaseModel):
    name: str
    description: Optional[str] = None
    user_role: str  # teacher, business, student, researcher, other
    audience: str   # students, executives, peers, self, general_public
    goal: str       # teach, present, learn, analyze, explain
    setting: str    # classroom, boardroom, study, paper, blog
    tone: Optional[str] = "professional"  # simple, professional, academic, casual
    depth: Optional[str] = "intermediate"  # beginner, intermediate, expert
    context_metadata: Optional[dict] = {}
    topics: Optional[List[str]] = []


class ProjectOut(BaseModel):
    id: int
    name: str
    description: Optional[str]
    user_role: str
    audience: str
    goal: str
    setting: str
    tone: str
    depth: str
    context_metadata: dict
    topics: List[str]
    owner_id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class ProjectVisualizationOut(BaseModel):
    id: int
    project_id: int
    slide_number: int
    title: str
    data: Any
    speaker_notes: Optional[str]
    annotations: List[dict]
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class GenerateProjectVisualizationsRequest(BaseModel):
    project_id: int
    user_query: str  # e.g., "Generate slides for teaching first ML class"
