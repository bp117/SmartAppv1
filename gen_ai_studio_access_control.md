
# Gen AI Studio Web App Access Control Table

| **Role/Access**           | **Home (Landing Page)** | **Workbench** | **Playground** | **How-to Guide** | **API References** | **Build Your Apps** | **Evaluate** | **Fine-Tuning** | **Administration** | **Prompt Management** |
|---------------------------|-------------------------|---------------|----------------|------------------|-------------------|---------------------|--------------|-----------------|--------------------|-----------------------|
| **Unauthenticated Users**  | ✅ (Read-only)           | ❌            | ❌             | ✅ (Read-only)    | ✅ (Read-only)     | ❌                  | ❌           | ❌              | ❌                 | ❌                    |
| **GenAI_Admin**            | ✅                       | ✅            | ✅             | ✅                | ✅                 | ✅                  | ✅           | ✅              | ✅                 | ✅                    |
| **GenAI_App_Developer**    | ✅                       | ✅            | ✅             | ✅                | ✅                 | ✅                  | Limited      | ❌              | ❌                 | Limited               |
| **GenAI_Evaluator**        | ✅                       | ✅            | ✅             | ✅                | ❌                 | ❌                  | ✅           | ❌              | ❌                 | Read-only             |
| **GenAI_Prompt_Engineer**  | ✅                       | ✅            | ✅             | ✅                | ✅                 | Read-only           | Read-only    | ❌              | ❌                 | ✅                    |
| **GenAI_Viewer**           | ✅                       | ✅            | ✅             | ✅                | ✅                 | Read-only           | Read-only    | ❌              | ❌                 | Read-only             |

### Explanation

- **Unauthenticated Users**:
   - **Home (Landing Page)**: Accessible to all unauthenticated users with read-only permissions (no ability to modify or interact).
   - **How-to Guide**: Read-only access to help documentation without requiring authentication.
   - **API References**: Available in read-only mode for unauthenticated users, useful for external developers wanting to integrate without login.
   - **No Access**: Unauthenticated users cannot access **Workbench**, **Playground**, or any features that involve app development, evaluation, or management.

- **Authenticated Users** (mapped to specific roles in AD groups like GenAI_Admin, GenAI_App_Developer, etc.):
   - Have varying levels of access based on their roles, as described in the previous permissions breakdown.
   - **GenAI_Admin** has full access to all areas.
   - **GenAI_App_Developer** can build and evaluate apps but doesn’t have fine-tuning or administrative rights.
   - **GenAI_Evaluator** can test and evaluate models but not manage apps or fine-tune them.
   - **GenAI_Prompt_Engineer** can create and manage prompts but only observe apps.
   - **GenAI_Viewer** has limited read-only access to observe the platform without making any changes.
