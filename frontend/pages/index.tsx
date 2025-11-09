export default function Home() {
  // This page immediately redirects to the static landing page
  if (typeof window !== 'undefined') {
    window.location.href = '/landing-page.html';
  }

  return null;
}
