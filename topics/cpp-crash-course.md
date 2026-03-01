# Topic: C++ Crash Course for Protocol Code Readers

## Why I Want to Learn This
Reading feedhandler and order gateway code in the APAC Exchange Connectivity plan keeps exposing C++ patterns I'm rusty on — templates, CRTP, reinterpret_cast, atomics. I need to be able to open any .h/.cpp file and understand what's happening without getting lost.

## Current Knowledge Level
Rusty intermediate — wrote C++ before (classes, pointers, STL) but haven't used it in a while.

## Goal
Read production C++ protocol code (feedhandlers, order gateways) confidently — understand every template, casting, and concurrency pattern without having to look up basic syntax.

## Resources
- cppreference.com (primary reference)
- "A Tour of C++" by Bjarne Stroustrup (refresher text)
- CppCon talks on CRTP, lock-free programming, low-latency C++
- rigtorp/SPSCQueue (open-source lock-free queue — real code to read)
- NASDAQ ITCH open-source parsers (real protocol code to read)

## Time Estimate
15 sessions (~3 weeks at 5x/week, 1.5hrs each)

## Priority
High — directly unblocks APAC Exchange Connectivity plan
