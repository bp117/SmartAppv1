
# Gen AI Studio Web App Access Control Table

| **Role/Access**           | **Home (Landing Page)** | **Workbench** | **Playground** | **How-to Guide** | **API References** | **Build Your Apps** | **Evaluate** | **Fine-Tuning** | **Administration** | **Prompt Management** | **Description** |
|---------------------------|-------------------------|---------------|----------------|------------------|-------------------|---------------------|--------------|-----------------|--------------------|-----------------------|------------------|
| **Unauthenticated Users**  | ✅ (Read-only)           | ❌            | ❌             | ✅ (Read-only)    | ✅ (Read-only)     | ❌                  | ❌           | ❌              | ❌                 | ❌                    | Limited read-only access to the landing page, how-to guide, and API references. Cannot interact with apps or models. |
| **GenAI_Admin**            | ✅                       | ✅            | ✅             | ✅                | ✅                 | ✅                  | ✅           | ✅              | ✅                 | ✅                    | Full control over the entire platform, including user management, apps, models, and prompts. Handles unauthorized access. |
| **GenAI_App_Developer**    | ✅                       | ✅            | ✅             | ✅                | ✅                 | ✅                  | Limited      | ❌              | ❌                 | Limited               | Focus on building apps. Limited access to evaluation and prompt management. No access to fine-tuning or administration. |
| **GenAI_Evaluator**        | ✅                       | ✅            | ✅             | ✅                | ❌                 | ❌                  | ✅           | ❌              | ❌                 | Read-only             | Focused on testing and evaluating models. Can view evaluation results but not build apps. No prompt editing rights. |
| **GenAI_Prompt_Engineer**  | ✅                       | ✅            | ✅             | ✅                | ✅                 | Read-only           | Read-only    | ❌              | ❌                 | ✅                    | Focus on creating and managing prompts. Can view apps and evaluation results to improve prompts. |
| **GenAI_Data_Scientist**   | ✅                       | ✅            | ✅             | ✅                | ✅                 | Limited             | ✅           | ✅              | ❌                 | Read-only             | Responsible for evaluating and fine-tuning models. Limited app-building rights and can view prompts. |
| **GenAI_Viewer**           | ✅                       | ✅            | ✅             | ✅                | ✅                 | Read-only           | Read-only    | ❌              | ❌                 | Read-only             | Read-only access to observe apps, models, and prompts. Cannot make changes or interact with models. |

### Explanation

**Unauthenticated Users**:
- **Home (Landing Page)**: Accessible to all unauthenticated users with read-only permissions (no ability to modify or interact).
- **How-to Guide**: Read-only access to help documentation without requiring authentication.
- **API References**: Available in read-only mode for unauthenticated users, useful for external developers wanting to integrate without login.
- **No Access**: Unauthenticated users cannot access **Workbench**, **Playground**, or any features that involve app development, evaluation, or management.

**Authenticated Users** (mapped to specific roles in AD groups like GenAI_Admin, GenAI_App_Developer, etc.):
- Have varying levels of access based on their roles, as described in the previous permissions breakdown.
- **GenAI_Admin** has full access to all areas.
- **GenAI_App_Developer** can build and evaluate apps but doesn’t have fine-tuning or administrative rights.
- **GenAI_Evaluator** can test and evaluate models but not manage apps or fine-tune them.
- **GenAI_Prompt_Engineer** can create and manage prompts but only observe apps.
- **GenAI_Data_Scientist** has access to evaluate models and fine-tune them, but limited access to app building.
- **GenAI_Viewer** has limited read-only access to observe the platform without making any changes.
