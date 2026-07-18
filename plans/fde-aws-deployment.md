# Learning Plan: FDE AWS Deployment

**Start date:** 2026-11-16
**Target completion:** ~2026-12-11 (4 weeks)
**Schedule:** 4 sessions/week, ~1.5 hours each
**Status:** not-started

> Approach: not a certification-style AWS survey. Every session touches a real running thing — a container, a deployed service, a policy that actually gates access — because the point is to be credible in front of a customer platform team, not to pass a multiple-choice exam. Each phase builds directly on the last: containerise first, get one thing deployed publicly to learn the primitives, then re-architect that same deployment privately, then bolt on the auth/secrets/CI layer a real engagement demands. The whole course culminates in redeploying the finance AI demo from `fde-production-ai-systems` (agents/RAG) and `typescript-crash-course` (front-end) as one enterprise-pattern system.

---

## Capstones by Phase

A phase isn't closed until its capstone artefact exists under `artefacts/fde-aws-deployment/phase-N/`.

| Phase | Capstone |
|---|---|
| Phase 1 (Docker) | `artefacts/fde-aws-deployment/phase-1/containerised-apps/` — Dockerfiles + `compose.yaml` for both the Python backend and the TypeScript front-end, multi-stage, pushed to ECR. Image size and layer-count noted in a short `NOTES.md`. |
| Phase 2 (AWS deploy path) | `artefacts/fde-aws-deployment/phase-2/ecs-deploy/` — the containerised app running on ECS Fargate behind a load balancer, backed by a managed datastore, with a least-privilege IAM policy set and CloudWatch log group. Includes a teardown script. |
| Phase 3 (Private patterns) | `artefacts/fde-aws-deployment/phase-3/private-architecture.md` — network diagram + written note: VPC endpoints/PrivateLink topology, private Bedrock access, and the data-egress argument for a bank security review. |
| Phase 4 (Auth/secrets/CI + flagship) | `artefacts/fde-aws-deployment/phase-4/flagship/` — the whole-course capstone: finance AI demo + RAG/agent system + TS front-end, redeployed with private VPC, private Bedrock access, SSO, Secrets Manager, and GitHub Actions CI/CD. Written architecture note + recorded walkthrough video. |

---

## Phase 1: Docker (Sessions 1-2)

Containers are the unit of deployment for everything that follows — every later phase assumes the app already runs correctly in a container. This phase is entirely about getting that right: images, layers, multi-stage builds, compose for local orchestration, and pushing to a real registry (ECR).

**Phase 1 capstone:** `artefacts/fde-aws-deployment/phase-1/containerised-apps/`

**Visual:** `docs/slides/fde-aws-deployment/phase-1.md` — 6-10 slides on image/layer fundamentals, multi-stage builds, and the registry push flow.

### Session 1: Images, layers, and multi-stage builds
**Objective:** Understand what a Docker image actually is and build small, correct images from scratch.
- [ ] Install Docker Desktop (or Docker Engine + CLI); verify with `docker run hello-world`
- [ ] Core concepts: image vs container, layers, the union filesystem, image caching and why layer order matters
- [ ] Write a naive single-stage `Dockerfile` for the Python backend from `fde-production-ai-systems`; build it, note the image size
- [ ] Rewrite as a multi-stage build: builder stage (installs deps, compiles) + slim runtime stage (`python:3.12-slim`); compare image size before/after
- [ ] `.dockerignore` — keep `.git`, `venv`, `node_modules`, secrets out of the build context
- [ ] Inspect layers with `docker history` and `dive` (or `docker buildx du`); identify the largest layer and shrink it
- [ ] Non-root user in the final image (`USER app`) — why running as root in a container is a real finding in a security review
- [ ] `HEALTHCHECK` instruction — what a platform team's orchestrator uses to decide a container is alive
- [ ] Environment variables vs baked-in config — never `COPY .env`, always inject at runtime
- [ ] Run the built image locally, hit its health endpoint, confirm logs go to stdout/stderr (not a file inside the container)
**Key concepts:** image layers, union filesystem, multi-stage builds, `.dockerignore`, non-root user, HEALTHCHECK, 12-factor config
**Resources:** Docker docs "Multi-stage builds", Docker docs "Best practices for writing Dockerfiles", `dive` (wagoodman/dive)

### Session 2: Compose, TypeScript container, and ECR
**Objective:** Orchestrate multi-container local dev with Compose, containerise the TS front-end, and push both images to a real registry.
- [ ] Write a multi-stage `Dockerfile` for the TypeScript front-end (`typescript-crash-course`): `node:20-alpine` builder + static/nginx or distroless runtime depending on whether it's a SPA or a Node server
- [ ] Write `compose.yaml` wiring backend + front-end + any local dependency (e.g. Postgres or Chroma) with named volumes and a shared network
- [ ] `docker compose up` — verify the front-end can reach the backend by service name (Compose's built-in DNS), not `localhost`
- [ ] Build-arg vs runtime-env distinction in Compose — which values are safe to bake in (build-time feature flags) vs must be injected (secrets, API base URLs that vary by environment)
- [ ] Create an ECR private repository (console or CLI); understand repository policies vs IAM permissions for push/pull
- [ ] Authenticate Docker to ECR (`aws ecr get-login-password`) and push both images; tag with both `latest` and a git-sha tag
- [ ] Image scanning — enable ECR basic scanning, review the vulnerability report on the pushed images, fix or justify any HIGH/CRITICAL findings
- [ ] Cost/cleanup note: ECR storage is billed per GB-month — delete throwaway tags after the session
**Key concepts:** Docker Compose, service DNS, build-time vs runtime config, ECR repositories, image push/pull auth, ECR image scanning
**Resources:** Docker Compose docs, AWS ECR "Getting started" guide, AWS CLI `ecr get-login-password` reference

---

## Phase 2: One AWS deploy path, end-to-end (Sessions 3-4)

The goal here is depth on exactly one path, not breadth across AWS's compute options. ECS Fargate is the choice: it is container-native (no EC2/AMI management, which is a distraction from the actual skill), it's the pattern most enterprise platform teams already run internally (vs App Runner, which is simpler but rarer in the wild and less negotiable when a customer already has an ECS-based platform), and every primitive learned here (task definitions, service, ALB, security groups) transfers directly to Phase 3's private variant. App Runner is mentioned for contrast but not built.

**Phase 2 capstone:** `artefacts/fde-aws-deployment/phase-2/ecs-deploy/`

**Visual:** `docs/slides/fde-aws-deployment/phase-2.md` — 6-10 slides on IAM fundamentals, the VPC subnet/security-group model, and the ECS Fargate deploy path.

### Session 3: IAM and VPC fundamentals, in service of the deploy
**Objective:** Learn only the IAM and VPC concepts needed to deploy safely — not the full service surface.
- [ ] IAM core model: users vs roles vs policies; why services (ECS tasks) assume roles rather than using long-lived access keys
- [ ] Write a least-privilege IAM policy by hand (JSON) for an ECS task role that can only read one specific S3 prefix and one specific Secrets Manager secret — no `*` resource, no `*` action
- [ ] IAM policy simulator or `aws iam simulate-principal-policy` — verify the policy denies what it should before deploying it
- [ ] VPC basics: what a VPC actually is, CIDR blocks, the default VPC vs a custom one
- [ ] Subnets: public vs private, and what "public" actually means (route table has a route to an Internet Gateway) — it is not an ACL, it's routing
- [ ] Route tables and Internet Gateway — trace a packet from a public subnet to the internet and back
- [ ] Security groups vs NACLs: security groups are stateful and attached to resources (the one you'll use constantly); NACLs are stateless and subnet-level (rarely touched day to day)
- [ ] Create a custom VPC by hand (or minimal Terraform/CDK if preferred) with 2 public + 2 private subnets across 2 AZs — this VPC is reused in Phase 3
- [ ] Write the note: for each of the IAM policy and security group you created, one sentence on what it prevents
**Key concepts:** IAM users/roles/policies, least privilege, policy simulation, VPC/CIDR, public vs private subnets, route tables, Internet Gateway, security groups vs NACLs
**Resources:** AWS IAM docs "Policies and permissions", AWS VPC docs "VPCs and subnets", AWS docs "Security groups vs network ACLs"

### Session 4: Deploy to ECS Fargate with managed data and logs
**Objective:** Get the containerised app running on Fargate, backed by a managed datastore, with logs flowing to CloudWatch.
- [ ] ECS core objects: cluster, task definition (the container spec), service (keeps N tasks running), and how Fargate removes the EC2/AMI layer entirely
- [ ] Write a task definition referencing the ECR image from Phase 1, the IAM task role from Session 3, and resource limits (CPU/memory) sized deliberately, not left at defaults
- [ ] Application Load Balancer in front of the service — target group, health check path, listener rule
- [ ] Security group chain: ALB SG allows 443 from internet -> ECS task SG allows traffic only from ALB SG -> nothing else can reach the task directly
- [ ] Managed data store decision: **RDS Postgres** if the app needs relational queries/joins (e.g. structured metadata, transactional writes) vs **DynamoDB** if it's key-value/document access at scale with simple access patterns. For the finance AI demo's metadata store, justify the pick in writing (this repo's RAG system likely favors Postgres for relational metadata alongside a vector extension, or DynamoDB if it's pure key-value session state — decide based on the actual `fde-production-ai-systems` schema)
- [ ] Stand up the chosen datastore in a private subnet only — no public accessibility, security group allows only the ECS task SG on the DB port
- [ ] Wire the connection string via environment variable sourced from Secrets Manager (not plaintext in the task definition) — full Secrets Manager depth comes in Phase 4, this is the minimal wiring
- [ ] CloudWatch Logs: configure the `awslogs` driver on the task definition, confirm application logs appear in a log group, set a retention period (never "never expire" — that's an unbounded cost)
- [ ] Deploy, hit the ALB DNS name, confirm the app works end-to-end against the managed datastore
- [ ] **Teardown checklist** (run every session that provisions billable resources — this is a personal AWS account): delete ECS service -> deregister task definitions -> delete ALB + target group -> delete RDS/DynamoDB -> delete NAT Gateway if one was created -> check CloudWatch log group retention -> review the AWS Cost Explorer "yesterday" view before ending the session
**Key concepts:** ECS cluster/task/service, Fargate, ALB + target groups, security group chaining, RDS vs DynamoDB selection, Secrets Manager env injection, CloudWatch Logs driver, cost teardown discipline
**Resources:** AWS ECS docs "Fargate", AWS docs "Application Load Balancer", AWS docs "Choosing between RDS and DynamoDB", AWS Cost Explorer

---

## Phase 3: Private deployment patterns (Sessions 5-6)

Everything in Phase 2 had a public ALB and public internet egress. That is not what an FDE deploys at a bank. This phase re-architects the same deployment so nothing crosses the VPC boundary — the single hardest and most valuable story an FDE has to tell: "your data never leaves your VPC."

**Phase 3 capstone:** `artefacts/fde-aws-deployment/phase-3/private-architecture.md`

**Visual:** `docs/slides/fde-aws-deployment/phase-3.md` — 6-10 slides on VPC endpoints, private Bedrock access, and the egress-control argument for a security review.

### Session 5: VPC endpoints, PrivateLink, and private Bedrock access
**Objective:** Understand how AWS services are reached without any traffic touching the public internet, and apply it to Bedrock specifically.
- [ ] The problem statement: by default, calling any AWS API (S3, Bedrock, Secrets Manager) from a private subnet either fails (no route out) or requires a NAT Gateway (traffic still egresses the VPC to AWS's public endpoints, just via a managed NAT) — neither is acceptable when the customer's requirement is "nothing leaves the VPC boundary"
- [ ] VPC Gateway Endpoints (S3, DynamoDB only) — free, route-table-based, traffic stays on the AWS backbone
- [ ] VPC Interface Endpoints (PrivateLink) — an ENI in your subnet with a private IP, backed by AWS's internal network, works for most other services including Bedrock and Secrets Manager
- [ ] Create a Bedrock VPC interface endpoint in the private subnets from Phase 2's VPC; attach a security group allowing only the ECS task SG
- [ ] Update DNS: interface endpoints use private DNS by default so `bedrock-runtime.<region>.amazonaws.com` resolves to the private IP inside the VPC — verify this with `nslookup` from inside a task (or a bastion/SSM session)
- [ ] Remove the NAT Gateway entirely from the Phase 2 architecture; redeploy the task; confirm Bedrock calls still succeed with zero public egress route
- [ ] VPC Flow Logs — enable them on the private subnets, confirm (by absence) that no flow record shows traffic to a public IP for the Bedrock calls
- [ ] Cost note: interface endpoints bill per-endpoint-hour + per-GB processed — cheaper than a NAT Gateway for API-shaped traffic, and the security story is strictly better, not just cheaper
**Key concepts:** VPC Gateway Endpoints, VPC Interface Endpoints (PrivateLink), private DNS resolution, Bedrock VPC endpoint, NAT Gateway removal, VPC Flow Logs verification
**Resources:** AWS docs "Interface VPC endpoints (AWS PrivateLink)", AWS Bedrock docs "Use Bedrock with VPC endpoints", AWS docs "VPC Flow Logs"

### Session 6: Data residency, egress control, and the security-review narrative
**Objective:** Convert the technical setup from Session 5 into the argument an FDE actually has to make in a room with a bank's security team.
- [ ] Data residency reasoning: which AWS region(s) the customer requires, how Bedrock model availability varies by region, and what "data processed by the model never leaves the region" means concretely (request/response payloads, not training data — Bedrock does not train on customer data by default, know this cold and know where AWS documents the guarantee)
- [ ] Egress control audit: enumerate every possible network path out of the VPC in the current architecture (interface endpoints, any remaining gateway endpoints, anything still routed through an IGW/NAT) and confirm each one is either removed or justified
- [ ] Security groups as the enforcement layer vs IAM as the authorization layer — a security reviewer will ask "what stops X" for both the network path and the identity path; have a one-line answer for each
- [ ] VPC endpoint policies — a second, resource-level control on top of the security group, restricting which specific Bedrock models/actions the endpoint can reach (defense in depth, not just "the SG allows it")
- [ ] Write the architecture note draft (feeds the Phase 3 capstone): a network diagram (ASCII or a simple drawing) showing VPC boundary, subnets, endpoints, and explicitly marking "no path to public internet" with the flow-log evidence from Session 5
- [ ] Anticipate the three questions every platform/security reviewer asks: (1) what's the blast radius if this task's IAM role is compromised, (2) where does data rest and is it encrypted (KMS at rest, TLS in transit — confirm both), (3) who can change this configuration and is that logged (CloudTrail)
- [ ] Enable CloudTrail (if not already on) and confirm the VPC/IAM/endpoint changes from this phase are logged — this is often the first thing a security reviewer checks
- [ ] Finalize `private-architecture.md` — this is the Phase 3 capstone, written at review-ready quality
**Key concepts:** data residency, Bedrock data-use guarantees, egress audit, VPC endpoint policies, defense in depth, blast radius reasoning, encryption at rest/in transit, CloudTrail
**Resources:** AWS Bedrock docs "Data protection", AWS docs "VPC endpoint policies", AWS docs "CloudTrail", AWS Well-Architected Framework — Security pillar (skim)

---

## Phase 4: Auth/SSO, secrets, and CI/CD (Sessions 7-8)

The last missing pieces before the app is genuinely enterprise-deployable: real authentication (not a hand-rolled login form), secrets handled the way an auditor expects, and a deploy pipeline that doesn't depend on someone typing `aws` commands from a laptop. Session 8 assembles everything from all four phases into the flagship capstone.

**Phase 4 capstone:** `artefacts/fde-aws-deployment/phase-4/flagship/`

**Visual:** `docs/slides/fde-aws-deployment/phase-4.md` — 6-10 slides on OAuth2/OIDC vs SAML, Cognito wiring, Secrets Manager patterns, and the CI/CD pipeline shape.

### Session 7: OAuth2/OIDC, SAML, Cognito, and Secrets Manager
**Objective:** Wire real authentication in front of the app and move all secrets out of environment variables into a managed secrets store.
- [ ] OAuth2 flows: authorization code flow (the one that matters for a web app with a backend), why implicit flow is deprecated, PKCE for public clients
- [ ] OIDC as the identity layer on top of OAuth2: ID token (who the user is) vs access token (what they can call) — a distinction that trips up almost everyone at first
- [ ] SAML at a level an FDE needs: XML-based, enterprise IdP standard (many banks still run ADFS/Okta via SAML for legacy reasons), the assertion/response flow, and why it coexists with OIDC rather than one replacing the other
- [ ] Set up Amazon Cognito: a User Pool (identity store) and configure it as either the IdP directly, or as a federation broker in front of an external IdP (SAML or OIDC) — for this exercise, federate against a free-tier external IdP (e.g. a test Okta/Auth0 tenant) to simulate "the customer already has their own IdP"
- [ ] Wire the TypeScript front-end to redirect to Cognito's hosted UI, handle the callback, and store the resulting tokens correctly (httpOnly cookie, not localStorage, for the access token)
- [ ] Backend token validation: verify the JWT signature against Cognito's JWKS endpoint, check `aud`/`iss`/`exp` claims — reject anything that doesn't validate, no silent fallback
- [ ] Secrets Manager: migrate every remaining plaintext env var (DB credentials, API keys) into Secrets Manager; set automatic rotation on at least the DB credential
- [ ] Parameter Store (SSM) vs Secrets Manager distinction: Parameter Store for non-secret config and cheaper secret storage without rotation, Secrets Manager when you need automatic rotation — pick correctly per value rather than defaulting everything to one
- [ ] Update the ECS task definition to pull secrets via the `secrets` field (resolved at task launch by the agent, never visible in the task definition JSON itself)
**Key concepts:** OAuth2 authorization code flow, PKCE, OIDC ID vs access tokens, SAML assertions, Cognito User Pool + federation, JWT validation via JWKS, Secrets Manager rotation, Parameter Store vs Secrets Manager
**Resources:** Cognito docs "Adding user pool sign-in through a third party", Auth0 "OAuth2 and OIDC in plain English" (or Okta's equivalent explainer), AWS docs "Secrets Manager rotation", AWS docs "Systems Manager Parameter Store"

### Session 8: CI/CD and flagship capstone assembly
**Objective:** Ship a minimal GitHub Actions pipeline, then assemble everything from Phases 1-4 into the whole-course flagship deployment.
- [ ] GitHub Actions workflow: on push to main, build the Docker image, push to ECR with a git-sha tag, update the ECS task definition, deploy via `aws ecs update-service --force-new-deployment`
- [ ] Authenticate GitHub Actions to AWS via OIDC federation (GitHub's OIDC provider + an IAM role with a trust policy scoped to this specific repo/branch) — no long-lived AWS access keys stored as GitHub secrets, this is itself a security-review talking point
- [ ] Scope the CI role's IAM policy to exactly what the pipeline needs: ECR push, ECS service update, nothing else
- [ ] Add a pipeline gate: build must pass tests before the ECR push step runs
- [ ] **Flagship assembly:** redeploy the finance AI demo (agents/RAG from `fde-production-ai-systems`) and the TypeScript front-end (`typescript-crash-course`) as one system, combining every prior phase: containerised (P1), on ECS Fargate with RDS/DynamoDB and CloudWatch (P2), fully private with VPC endpoints and private Bedrock access (P3), fronted by Cognito SSO with secrets in Secrets Manager (P4), deployed via the GitHub Actions pipeline built this session
- [ ] Write the architecture note: consolidate the Phase 3 network diagram, add the auth flow diagram, the CI/CD flow, and an explicit "what a platform team would ask, and the answer" section
- [ ] Record the walkthrough video: narrate a deploy (triggered via the pipeline or shown end-to-end) as if presenting to a customer's security/platform team — cover the network boundary, the auth flow, and the deploy mechanism in under 10 minutes
- [ ] Full teardown of every resource created across all 8 sessions; confirm via Cost Explorer that nothing is still billing
**Key concepts:** GitHub Actions to ECR/ECS pipeline, GitHub OIDC federation to AWS, scoped CI IAM role, test gate before deploy, full-stack private enterprise deployment, architecture note authoring, technical walkthrough presentation
**Resources:** GitHub Actions docs "Configuring OpenID Connect in Amazon Web Services", AWS docs "Deploying to Amazon ECS from GitHub Actions", `fde-production-ai-systems` plan (this repo), `typescript-crash-course` plan (this repo)

---

## Closing the loop

- **Phases 1-2** are the general-purpose AWS deploy skill — reusable for any future container-based service, not just this course's capstone.
- **Phase 3** is the differentiator that actually matters for FDE work in finance: most engineers can get something running on AWS; far fewer can architect and *explain* a private deployment a bank's security team will sign off on.
- **Phase 4** closes with the system this course exists to deploy: the agent/RAG system from `fde-production-ai-systems` behind the front-end from `typescript-crash-course`, running as one enterprise-pattern deployment with a review-ready architecture note and a recorded walkthrough — the artefact that actually gets shown in an FDE interview or a real customer pilot kickoff.
- **Cost hygiene throughout:** every session that provisions billable resources ends with a teardown step (explicit checklist in Session 4, repeated implicitly every session after). This is a personal AWS account — nothing survives past the session that isn't needed for the next one, and Cost Explorer gets checked before closing out.
