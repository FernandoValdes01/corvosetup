# Frontend quality

Before designing, inspect the existing layout, components, tokens, colors, typography, spacing, similar pages, UI libraries, breakpoints, and interaction patterns. Reuse appropriate components; do not duplicate them. Question the existing system only when the request calls for a redesign or it cannot satisfy an acceptance criterion.

Prefer professional, restrained, product-specific UI. Avoid decorative glass, gratuitous gradients, nested cards, oversized shadows, badge overload, purposeless floating elements, futuristic AI styling, and unnecessary motion. Minimal does not mean empty; modern does not mean futuristic.

Implement coherent hover, focus, active, selected, disabled, loading, empty, and error states when relevant. Preserve semantic HTML, keyboard access, visible focus, contrast, responsive behavior, and content hierarchy.

## Visual verification

When the application can be rendered, the orchestrator must inspect the real result at representative desktop and mobile sizes. Check overflow, alignment, spacing, hierarchy, density, interaction states, and obvious regressions. A successful build is not visual proof.

OpenCode workers may not have access to T3Code's collaborative preview. In that case, Sol performs the preview. If nobody can see a rendered interface, report exactly:

```text
VISUAL VERIFICATION: NOT AVAILABLE
```

Never imply visual inspection from source review, screenshots not actually opened, or build success.
