import Layout from "@theme/Layout";

export default function Home(): JSX.Element {
  return (
    <Layout title="Discovery Intelligence" description="Documentation hub for the legal discovery platform">
      <main style={{ padding: "4rem 0" }}>
        <div className="container">
          <h1 style={{ fontSize: "3rem", marginBottom: "1rem" }}>Discovery Intelligence Docs</h1>
          <p style={{ fontSize: "1.2rem", maxWidth: "48rem" }}>
            Explore platform usage, product release notes, and best practices for orchestrating automated legal discovery. Use
            the sidebar to jump directly into the guides most relevant to your role.
          </p>
        </div>
      </main>
    </Layout>
  );
}
