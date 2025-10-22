# Workspace Architecture Enhancement Plan

## Volume I: Foundational Scaffolding
### Chapter 1: Frontend Application Bootstrap
#### Section 1.1: Directory Genesis
##### Paragraph 1.1.1: Create `apps/frontend`
- [x] Command: `mkdir -p apps/frontend`
- [x] Ensure `.gitkeep` unnecessary once populated with project files.
##### Paragraph 1.1.2: Establish README
- [x] Author comprehensive README detailing stack (Vite, React, Tailwind, Radix UI) and bootstrap steps.
#### Section 1.2: Application Realization
##### Paragraph 1.2.1: Initialize Vite React TypeScript project
- [x] Use `npm create vite@latest` equivalent via manual scaffolding to avoid network dependencies.
- [x] Configure `package.json`, `tsconfig`, `vite.config.ts` with React + SWC template characteristics.
##### Paragraph 1.2.2: Integrate Tailwind CSS
- [x] Add Tailwind, PostCSS, Autoprefixer deps.
- [x] Create `tailwind.config.ts` referencing Radix colors/plugins as needed.
- [x] Configure `postcss.config.cjs` and `src/index.css` with Tailwind directives.
##### Paragraph 1.2.3: Integrate Radix UI primitives
- [x] Install Radix React packages minimal baseline (e.g., `@radix-ui/react-toast`).
- [x] Demonstrate usage within `App.tsx` via simple component.
##### Paragraph 1.2.4: Developer Experience
- [x] Add ESLint + Prettier configuration consistent with repo standards.
- [x] Provide npm scripts for lint, type-check, test, format, dev, build.
- [x] Configure Vitest for unit tests.

### Chapter 2: Infrastructure & Testing Structure
#### Section 2.1: Infra Directory
##### Paragraph 2.1.1: Create `infra` directory with README outlining Terraform/Helm expectations.
- [x] Author README describing Terraform + Helm usage patterns.
##### Paragraph 2.1.2: Scaffold Terraform baseline
- [x] Introduce `main.tf`, `providers.tf`, and backend configuration with realistic resources.
##### Paragraph 2.1.3: Scaffold Helm chart baseline
- [x] Create `helm/platform` chart with deployment, service, and ingress templates plus environment values.

#### Section 2.2: Tests Directory
##### Paragraph 2.2.1: Create `tests` with README describing integration suites.
- [x] Document integration testing approach and commands.
##### Paragraph 2.2.2: Provide example integration test harness using pytest aligned with backend services.
- [x] Add fixtures bootstrapping FastAPI app and a retrieval flow scenario.

### Chapter 3: Documentation System
#### Section 3.1: Docs Directory enhancements
##### Paragraph 3.1.1: Ensure docs contains README describing MkDocs and Docusaurus usage.
- [x] Provide documentation README with contribution standards.
##### Paragraph 3.1.2: Provide baseline configuration for MkDocs and Docusaurus.
- [x] Add MkDocs config & starter pages along with a Docusaurus site scaffold.

### Chapter 4: Tooling & Automation
#### Section 4.1: Root Task Runner
##### Paragraph 4.1.1: Evaluate existing tooling (Just, Make) to avoid duplication.
- [x] Adopt `just` for cross-platform command orchestration.
##### Paragraph 4.1.2: Implement commands orchestrating lint, type-check, format, test for backend/frontend.
- [x] Define just recipes covering installs, linting, formatting, type-checking, and testing.
##### Paragraph 4.1.3: Provide meta tasks for `ci` aggregator referencing structure check.
- [x] Compose `ci` recipe invoking installs, checks, and tests for every workspace.

#### Section 4.2: CI Structure Validation
##### Paragraph 4.2.1: Create script verifying directories exist and contain expected config files.
- [x] Implement `tools/check_workspace_structure.py` with strict validations.
##### Paragraph 4.2.2: Integrate script into CI (GitHub Actions).
- [x] Add CI workflow executing the structure check and orchestration recipes.

## Volume II: Execution Checkpoints
### Chapter 5: Audit existing backend tooling
- [x] Inspect `apps/backend` dependencies, test commands, lint config to integrate with root runner.

### Chapter 6: README Enhancements
- [x] Update root README with workspace overview, bootstrap instructions for each app, referencing new task runner.
- [x] Ensure new READMEs cross-reference relevant tooling.

## Volume III: Verification & Polish
### Chapter 7: Run automated checks
- [x] Execute `npm`, `just`, `pytest` etc verifying functionality.
### Chapter 8: Final Review
- [x] Double-pass diff review ensuring no placeholders, high quality.
