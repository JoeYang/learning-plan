# Topic: APAC Exchange Connectivity

## Why I Want to Learn This
Joining a trading team that runs exchange connectivity for APAC futures exchanges (SGX, JPX/OSE, HKEX). Need to read and understand existing production C++ code for feedhandlers and order gateways — not design from scratch, but be functional with the codebase and protocols the team uses daily.

## Current Knowledge Level
Intermediate. Built a CME MDP 3.0 feed handler (binary protocol parsing, order books, recovery state machines). Can read C++ somewhat (Java/C# background). Understand market data concepts but haven't worked with APAC exchange protocols (ITCH, OUCH, OMD, OAPI) or exchange-specific session management.

## Goal
Be functionally competent with SGX Titan (ITCH/OUCH), JPX J-GATE (ITCH/OUCH for OSE derivatives), and HKEX (OMD-D/OCG). Specifically: read feedhandler and order gateway code, understand protocol message flows, know how session management and recovery work, and be able to trace a trade lifecycle from market data tick to order fill. Know what's different across exchanges and why.

## Resources
- Exchange specifications: SGX Titan ITCH/OUCH, JPX J-GATE specs, HKEX OMD-D/OCG documentation
- Protocol references: NASDAQ ITCH 5.0 spec, OUCH 4.2 spec, SoupBinTCP spec, FIX 4.2/5.0 specs
- Books: Johnson "Algorithmic Trading and DMA" (exchange connectivity chapters)
- Internal: team's existing feedhandler and order gateway codebases

## Time Estimate
20 sessions over 4 weeks (5 sessions/week, ~1.5 hours each)

## Priority
high
