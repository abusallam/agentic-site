
# File Mapping and Reorganization Plan

## Summary
- Total Operations: 1343
- Files to Move: 217
- Files to Delete: 0
- Conflicts Found: 24

## Directory Structure to Create
- **frontend/**: Next.js application and React components
  - app/
  - components/
  - lib/
  - hooks/
  - styles/
  - public/
- **backend/**: Python ADK agent system (keep current agent/ structure)
  - agent/
- **infrastructure/**: Deployment, Docker, and infrastructure code
  - docker/
  - scripts/
  - nginx/
  - ssl/
  - monitoring/
  - ansible/
- **docs/**: Documentation and guides
  - deployment/
  - monitoring/
  - troubleshooting/
- **tests/**: Integration and E2E tests (keep current structure)
  - e2e/
  - integration/
  - unit/
- **tools/**: Development tools and utilities (keep current structure)
  - database/
  - monitoring/
  - security/

## File Moves
- `jest.config.js` → `frontend/jest.config.js` (Organize frontend files)
- `tailwind.config.ts` → `frontend/tailwind.config.ts` (Organize frontend files)
- `postcss.config.mjs` → `frontend/postcss.config.mjs` (Organize frontend files)
- `jest.setup.js` → `frontend/jest.setup.js` (Organize frontend files)
- `playwright.config.ts` → `frontend/playwright.config.ts` (Organize frontend files)
- `next.config.mjs` → `frontend/next.config.mjs` (Organize frontend files)
- `app/error.tsx` → `frontend/app/error.tsx` (Organize frontend files)
- `app/loading.tsx` → `frontend/app/loading.tsx` (Organize frontend files)
- `app/globals.css` → `frontend/app/globals.css` (Organize frontend files)
- `app/page.tsx` → `frontend/app/page.tsx` (Organize frontend files)
- `app/layout.tsx` → `frontend/app/layout.tsx` (Organize frontend files)
- `app/css-fix.css` → `frontend/app/css-fix.css` (Organize frontend files)
- `app/contact/page.tsx` → `frontend/app/contact/page.tsx` (Organize frontend files)
- `app/about/page.tsx` → `frontend/app/about/page.tsx` (Organize frontend files)
- `app/customer/page.tsx` → `frontend/app/customer/page.tsx` (Organize frontend files)
- `app/customer/dashboard/page.tsx` → `frontend/app/customer/dashboard/page.tsx` (Organize frontend files)
- `app/auth/login/page.tsx` → `frontend/app/auth/login/page.tsx` (Organize frontend files)
- `app/auth/signup/page.tsx` → `frontend/app/auth/signup/page.tsx` (Organize frontend files)
- `app/admin/page.tsx` → `frontend/app/admin/page.tsx` (Organize frontend files)
- `app/admin/dashboard/page.tsx` → `frontend/app/admin/dashboard/page.tsx` (Organize frontend files)
... and 197 more moves

## Files to Delete

## Conflicts to Resolve
- **Keep**: `archive/cleanup/cleanup_log_20250722_012646.json`
  **Delete**: `archive/cleanup/cleanup_log_20250722_010302.json`
  **Reason**: Duplicate files with same content (hash: 34099e69)

- **Keep**: `archive/development/fix_translation_and_styling.py`
  **Delete**: `archive/deployment/docker_installation_fixed.py`
  **Reason**: Duplicate files with same content (hash: d41d8cd9)

- **Keep**: `components/ui/use-mobile.tsx`
  **Delete**: `hooks/use-mobile.tsx`
  **Reason**: Duplicate files with same content (hash: 209b5193)

- **Keep**: `archive/development/fix_translation_and_styling.py`
  **Delete**: `n8n-mcp/data/nodes.db-wal`
  **Reason**: Duplicate files with same content (hash: d41d8cd9)

- **Keep**: `archive/development/fix_translation_and_styling.py`
  **Delete**: `n8n-mcp/data/nodes.db.backup`
  **Reason**: Duplicate files with same content (hash: d41d8cd9)

- **Keep**: `agent/specialized_agents/technical_agent.py`
  **Delete**: `archive/development/fix_translation_and_styling.py`
  **Reason**: Duplicate files with same content (hash: d41d8cd9)

- **Keep**: `agent/specialized_agents/customer_support_agent.py`
  **Delete**: `archive/development/fix_translation_and_styling.py`
  **Reason**: Duplicate files with same content (hash: d41d8cd9)

- **Keep**: `public/temp-logo.png`
  **Delete**: `public/logo.webp`
  **Reason**: Duplicate files with same content (hash: cde7af44)

- **Keep**: `.husky/_/prepare-commit-msg`
  **Delete**: `.husky/_/pre-merge-commit`
  **Reason**: Duplicate files with same content (hash: 0b71c2e7)

- **Keep**: `.husky/_/prepare-commit-msg`
  **Delete**: `.husky/_/applypatch-msg`
  **Reason**: Duplicate files with same content (hash: 0b71c2e7)

- **Keep**: `.husky/_/prepare-commit-msg`
  **Delete**: `.husky/_/pre-rebase`
  **Reason**: Duplicate files with same content (hash: 0b71c2e7)

- **Keep**: `.husky/_/prepare-commit-msg`
  **Delete**: `.husky/_/post-rewrite`
  **Reason**: Duplicate files with same content (hash: 0b71c2e7)

- **Keep**: `.husky/_/prepare-commit-msg`
  **Delete**: `.husky/_/pre-auto-gc`
  **Reason**: Duplicate files with same content (hash: 0b71c2e7)

- **Keep**: `.husky/_/prepare-commit-msg`
  **Delete**: `.husky/_/post-merge`
  **Reason**: Duplicate files with same content (hash: 0b71c2e7)

- **Keep**: `.husky/_/prepare-commit-msg`
  **Delete**: `.husky/_/post-commit`
  **Reason**: Duplicate files with same content (hash: 0b71c2e7)

- **Keep**: `.husky/_/prepare-commit-msg`
  **Delete**: `.husky/_/pre-push`
  **Reason**: Duplicate files with same content (hash: 0b71c2e7)

- **Keep**: `.husky/_/prepare-commit-msg`
  **Delete**: `.husky/_/post-applypatch`
  **Reason**: Duplicate files with same content (hash: 0b71c2e7)

- **Keep**: `.husky/_/prepare-commit-msg`
  **Delete**: `.husky/_/pre-commit`
  **Reason**: Duplicate files with same content (hash: 0b71c2e7)

- **Keep**: `.husky/_/prepare-commit-msg`
  **Delete**: `.husky/_/post-checkout`
  **Reason**: Duplicate files with same content (hash: 0b71c2e7)

- **Keep**: `.husky/_/prepare-commit-msg`
  **Delete**: `.husky/_/commit-msg`
  **Reason**: Duplicate files with same content (hash: 0b71c2e7)

- **Keep**: `.husky/_/prepare-commit-msg`
  **Delete**: `.husky/_/pre-applypatch`
  **Reason**: Duplicate files with same content (hash: 0b71c2e7)

- **Keep**: `agent/test_n8n_mcp_integration.py`
  **Delete**: `tests/integration/agent/test_n8n_mcp_integration.py`
  **Reason**: Duplicate files with same content (hash: cd906905)

- **Keep**: `agent/test_multi_agent_system.py`
  **Delete**: `tests/integration/agent/test_multi_agent_system.py`
  **Reason**: Duplicate files with same content (hash: a3876974)

- **Keep**: `agent/test_agent.py`
  **Delete**: `tests/integration/agent/test_agent.py`
  **Reason**: Duplicate files with same content (hash: 4edad3bb)


## Files to Preserve
- 1126 files will be preserved in their current locations
