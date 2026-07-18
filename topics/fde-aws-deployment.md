# Topic: FDE AWS Deployment

## Why I Want to Learn This
Cloud/deployment is my biggest gap on the path to Forward Deployed Engineer (FDE) work in AI, finance-vertical. I can build the AI system (agents, RAG, the demo front-end) but I have no real experience getting it running inside a customer's environment. FDEs live at exactly that seam: a bank's platform team hands you a locked-down AWS account with no public internet egress, opinionated IAM, and a security review gate, and you're expected to land a working system and defend the architecture in the room. Track 4 of my FDE path — after `fde-production-ai-systems` (the system) and `typescript-crash-course` (the front-end) — closes that gap by taking what I've already built and deploying it the way a real enterprise engagement would require.

## Current Knowledge Level
none — essentially no cloud or deployment experience. Strong C++ (low-latency trading), strong Python, working TypeScript. Comfortable with systems concepts (networking, processes, concurrency) but have never provisioned cloud infrastructure, written IAM policy, or deployed a container to a managed runtime.

## Goal
Be able to:
1. Containerise an existing Python/TypeScript application correctly (multi-stage builds, small images, no secrets baked in) and push it to a registry.
2. Stand up one AWS deploy path end-to-end from first principles — IAM, VPC basics, a managed compute target, a managed data store, logs — and explain every piece.
3. Design and justify a **private** deployment: no public ingress/egress, private model access (Bedrock via VPC endpoint / PrivateLink), and articulate the "your data never leaves your VPC" story a bank's security team needs to hear before they'll approve a pilot.
4. Wire up authentication a real customer would require (OIDC/SAML via an IdP, not a hand-rolled login) and handle secrets the way an auditor expects (Secrets Manager, not `.env` files in the image).
5. Stand up minimal CI/CD (GitHub Actions → ECR → ECS) so a deploy is a `git push`, not a manual `aws` command sequence typed live in a client meeting.
6. Talk to a customer platform team credibly: know the vocabulary, know what they'll ask, know where the actual risk is (data egress, blast radius, least privilege) versus what's just AWS trivia.

This is explicitly **not** an AWS certification survey. Anything that isn't load-bearing for "deploy an AI system into a locked-down enterprise AWS account" is out of scope.

## Capstone: what artefact proves mastery?
**End-to-end vertical flagship:** redeploy the existing finance AI demo (RAG/agent system from `fde-production-ai-systems`, front-end from `typescript-crash-course`) into an enterprise-pattern AWS deployment — private VPC, private Bedrock model access via VPC endpoint, SSO in front of the app — plus:
- A written architecture note, at the standard a customer platform team could review and approve, covering the network diagram, IAM boundaries, data flow (with the egress story explicit), and the auth flow.
- A recorded walkthrough video: deploy from a clean slate (or from CI) and narrate the architecture as if presenting to a client's security/platform team.

Per-phase artefacts land under `artefacts/fde-aws-deployment/phase-N/`; the Phase 4 / Session 8 artefact is the flagship above, assembled from the working pieces built in Phases 1-3.

## Resources (optional)
- AWS official docs: ECS, Fargate, App Runner, ECR, VPC, PrivateLink, Bedrock, Cognito, Secrets Manager, IAM
- Docker docs: multi-stage builds, BuildKit
- GitHub Actions docs: OIDC federation to AWS (no long-lived AWS keys in CI)
- `fde-production-ai-systems` (this repo) — the system being deployed
- `typescript-crash-course` (this repo) — the front-end being deployed
- AWS Well-Architected Framework — Security and Reliability pillars (skim, not the full survey)

## Time Estimate
8 sessions, ~1.5 hours each, 4 sessions/week — roughly 2 weeks (2026-11-16 to 2026-12-11 target).

## Priority
high
