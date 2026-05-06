Project Documentation: Priority vs. SRTF Simulator
1. Functional Overview
The simulator is designed to evaluate and compare process scheduling behavior using two distinct preemption policies:  

SRTF (Shortest Remaining Time First): Implements immediate preemption based on the smallest remaining burst time to optimize system efficiency.  

Preemptive Priority: Implements policy-driven preemption based on externally assigned priority values.  

2. Core Deliverables (Per Instructor Requirements)
Input Validation: The UI handles invalid data types to maintain application stability during live demonstrations.  

One-Click Reset: A dedicated system re-initialization routine allows for consecutive simulation runs without application restarts.  

Scenario Automation: Pre-loaded test cases are integrated as quick-access buttons to streamline the instructor's evaluation process.  

3. Strategic Test Scenarios (image_921cd3.png Compliance)
Scenario A (Baseline): Validates standard operational metrics (WT, TAT, RT) across a mixed workload.  

Scenario B (Priority-Time Conflict): Demonstrates the performance gap when high-priority tasks have long burst times vs. short low-priority tasks.  

Scenario C (Starvation Risk): Specifically highlights the critical weakness of Priority scheduling where low-priority processes remain idle.  

Scenario D (Input Integrity): Proves system resilience against invalid input parameters.  

4. Technical Summary for Discussion
Metric Analysis: SRTF is mathematically optimal for minimizing Average Waiting Time, while Priority is superior for Mission-Critical task execution.  

Trade-off: The primary trade-off observed is between Algorithmic Efficiency (SRTF) and Policy Enforcement (Priority).
