# Documentation Systems

The documentation stack blends **MkDocs** for lightweight architecture notes with **Docusaurus** for the long-form product knowledge base.

## MkDocs (Operational Notes)
- Configuration lives in `docs/mkdocs.yml` (to be expanded as features land).
- Author task-oriented runbooks and ADRs in `docs/notes/**/*.md`.
- Build locally with `mkdocs serve` for fast iteration.

## Docusaurus (Product Knowledge Base)
- Source content belongs in `docs/docusaurus` with versioned API references and tutorials.
- Use `npm install` followed by `npm run start` inside `docs/docusaurus` to develop the knowledge base.
- Trigger static builds with `npm run build`; publish artifacts from `build/`.

## Contribution Standards
1. Every new feature ships with a MkDocs changelog entry summarizing architectural impacts.
2. Long-form, externally facing material belongs in Docusaurus and should include screenshots or diagrams when possible.
3. Validate broken links with `mkdocs build --strict` and `npm run lint` in the Docusaurus app before merging.

## Roadmap
- [ ] Wire MkDocs navigation to the new multi-agent orchestration guides.
- [ ] Stand up a Docusaurus versioned docs pipeline with GitHub Pages deployment.
