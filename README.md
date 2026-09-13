# InstaSafe-Auth-System
Secure Flask authentication and RBAC system using JWT, bcrypt and MySQL.
## Security Design Notes

**Why JWT (JSON Web Tokens):** Chosen for stateless authentication — the server doesn't
need to store session state, which keeps the API simple to scale horizontally. Each
token carries the user's identity and role claims, verified via signature on every
request rather than a server-side session lookup.

**Why bcrypt for password hashing:** bcrypt is an adaptive hashing algorithm — its
cost factor can be increased over time as hardware gets faster, and it includes
per-password salting by design, which protects against rainbow-table attacks and
makes brute-forcing computationally expensive even if the password database is
ever exposed.

**Why Role-Based Access Control (RBAC):** Enforces least-privilege access — users
only get the permissions their role requires (e.g., admin vs. standard user),
implemented via custom decorators on protected routes so authorization logic
stays centralized and auditable rather than scattered through business logic.

**Token handling:** [Describe here exactly what you built — e.g., token expiry
duration, whether you implemented refresh tokens, where the token is stored
client-side, and how expired/invalid tokens are rejected.]
