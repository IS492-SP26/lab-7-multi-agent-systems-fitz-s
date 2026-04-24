"""
CrewAI Multi-Agent Demo: Software Architecture Design (Exercise 4)

This demonstrates CrewAI's task-based multi-agent orchestration applied to
Software Architecture Design. Each agent has a specific task executed in
sequential order, contrasting with AutoGen's conversational approach.

Agents:
1. RequirementsAgent - Gathers and analyzes system requirements
2. ArchitectAgent - Designs the system architecture
3. ImplementationAgent - Plans the implementation strategy
4. RiskAgent - Evaluates risks and proposes mitigations

Configuration:
- Uses shared configuration from the root .env file
"""

import os
import sys
from pathlib import Path
from datetime import datetime
from crewai import Agent, Task, Crew
from crewai.tools import tool

# Add parent directory to path to import shared_config
sys.path.insert(0, str(Path(__file__).parent.parent))

# Import shared configuration
from shared_config import Config, validate_config


# ============================================================================
# TOOLS
# ============================================================================

@tool
def analyze_tech_landscape(technology_area: str) -> str:
    """
    Analyze the current technology landscape for a given area.
    Returns information about popular frameworks, tools, and best practices.
    """
    tech_data = {
        "real-time collaboration": {
            "frameworks": [
                {"name": "Yjs", "type": "CRDT Library", "language": "JavaScript/TypeScript", "description": "High-performance CRDT implementation for real-time collaboration. Used by many editors.", "popularity": "Very High"},
                {"name": "Automerge", "type": "CRDT Library", "language": "Rust/JavaScript", "description": "JSON-like CRDT data structure for peer-to-peer collaboration.", "popularity": "High"},
                {"name": "ShareDB", "type": "OT Framework", "language": "JavaScript", "description": "Operational Transformation engine for real-time JSON/text editing.", "popularity": "Medium"},
                {"name": "Liveblocks", "type": "SaaS Platform", "language": "TypeScript", "description": "Managed real-time collaboration infrastructure with presence and storage.", "popularity": "Growing"},
            ],
            "patterns": ["CRDT (Conflict-free Replicated Data Types)", "Operational Transformation (OT)", "Event Sourcing", "WebSocket pub/sub"],
            "considerations": ["Latency < 100ms for real-time feel", "Conflict resolution strategy", "Offline support and sync", "Document size limits"],
        },
        "scalable backend": {
            "frameworks": [
                {"name": "Kubernetes", "type": "Container Orchestration", "language": "Go", "description": "Industry standard for container orchestration and auto-scaling.", "popularity": "Very High"},
                {"name": "Apache Kafka", "type": "Event Streaming", "language": "Java/Scala", "description": "Distributed event streaming platform for high-throughput data pipelines.", "popularity": "Very High"},
                {"name": "Redis", "type": "In-memory Cache/DB", "language": "C", "description": "Ultra-fast in-memory data store with pub/sub capabilities.", "popularity": "Very High"},
                {"name": "PostgreSQL", "type": "Relational DB", "language": "C", "description": "Advanced open-source relational database with strong consistency.", "popularity": "Very High"},
            ],
            "patterns": ["Microservices Architecture", "Event-Driven Architecture", "CQRS", "Database sharding"],
            "considerations": ["Horizontal scaling strategy", "Data consistency vs. availability tradeoffs", "Service mesh for inter-service communication", "Observability and monitoring"],
        },
        "security": {
            "frameworks": [
                {"name": "OAuth 2.0 / OIDC", "type": "Auth Protocol", "language": "Protocol", "description": "Industry standard for authorization and authentication.", "popularity": "Very High"},
                {"name": "Vault by HashiCorp", "type": "Secrets Management", "language": "Go", "description": "Secrets management and data encryption platform.", "popularity": "High"},
                {"name": "AWS IAM", "type": "Access Control", "language": "Cloud Service", "description": "Fine-grained access control for cloud resources.", "popularity": "Very High"},
                {"name": "OWASP ZAP", "type": "Security Testing", "language": "Java", "description": "Open-source web application security scanner.", "popularity": "High"},
            ],
            "patterns": ["Zero Trust Architecture", "Role-Based Access Control (RBAC)", "End-to-end encryption", "Security-by-design"],
            "considerations": ["Data encryption at rest and in transit", "Compliance (SOC2, GDPR)", "Penetration testing cadence", "Incident response plan"],
        },
    }

    # Find matching data
    key = None
    for k in tech_data:
        if k in technology_area.lower():
            key = k
            break
    if not key:
        key = "scalable backend"  # default

    data = tech_data[key]

    output = f"Technology Landscape Analysis: {technology_area}\n"
    output += f"{'='*60}\n"

    output += f"\n--- Popular Frameworks & Tools ---\n"
    for i, fw in enumerate(data["frameworks"], 1):
        output += f"\n{i}. {fw['name']} ({fw['type']})\n"
        output += f"   Language: {fw['language']} | Popularity: {fw['popularity']}\n"
        output += f"   {fw['description']}\n"

    output += f"\n--- Key Architecture Patterns ---\n"
    for p in data["patterns"]:
        output += f"  • {p}\n"

    output += f"\n--- Critical Considerations ---\n"
    for c in data["considerations"]:
        output += f"  ⚠ {c}\n"

    return output


@tool
def evaluate_architecture_risks(architecture_type: str) -> str:
    """
    Evaluate common risks for a given architecture type.
    Returns risk assessment with likelihood, impact, and mitigations.
    """
    risks_data = {
        "distributed": [
            {"risk": "Network Partition Failures", "likelihood": "Medium", "impact": "High", "description": "Network splits causing data inconsistency between services.", "mitigation": "Implement circuit breakers, use eventual consistency with CRDTs, and design for partition tolerance."},
            {"risk": "Data Consistency Issues", "likelihood": "High", "impact": "High", "description": "Maintaining consistency across distributed data stores.", "mitigation": "Use saga pattern for distributed transactions, implement idempotent operations, and establish clear consistency boundaries."},
            {"risk": "Cascading Failures", "likelihood": "Medium", "impact": "Critical", "description": "Single service failure propagating through the system.", "mitigation": "Implement bulkheads, circuit breakers, and retry policies with exponential backoff."},
            {"risk": "Operational Complexity", "likelihood": "High", "impact": "Medium", "description": "Difficulty in monitoring, debugging, and maintaining distributed systems.", "mitigation": "Invest in observability (distributed tracing, centralized logging), use service mesh, and automate deployment."},
            {"risk": "Performance Bottlenecks at Scale", "likelihood": "Medium", "impact": "High", "description": "Hot spots and resource contention under high load.", "mitigation": "Load testing, horizontal auto-scaling, database read replicas, and caching layers."},
        ],
        "monolithic": [
            {"risk": "Scaling Limitations", "likelihood": "High", "impact": "High", "description": "Inability to scale individual components independently.", "mitigation": "Plan modular boundaries for future extraction into services."},
            {"risk": "Deployment Risk", "likelihood": "Medium", "impact": "Medium", "description": "Full redeployment needed for any change.", "mitigation": "Feature flags and blue-green deployments."},
        ],
    }

    key = "distributed" if "distribut" in architecture_type.lower() or "micro" in architecture_type.lower() else "monolithic"
    risks = risks_data[key]

    output = f"Risk Assessment: {architecture_type}\n"
    output += f"{'='*60}\n"
    for i, risk in enumerate(risks, 1):
        output += f"\n{i}. {risk['risk']}\n"
        output += f"   Likelihood: {risk['likelihood']} | Impact: {risk['impact']}\n"
        output += f"   Description: {risk['description']}\n"
        output += f"   Mitigation: {risk['mitigation']}\n"

    return output


# ============================================================================
# AGENT DEFINITIONS
# ============================================================================

def create_requirements_agent():
    """Create the Requirements Analyst agent."""
    return Agent(
        role="Requirements Analyst",
        goal="Define comprehensive functional and non-functional requirements "
             "for a real-time collaborative document editing platform.",
        backstory="You are a senior requirements analyst with 15 years of experience "
                  "in software systems. You have worked on collaboration tools, SaaS platforms, "
                  "and high-scale consumer applications. You excel at translating business "
                  "needs into precise technical requirements. You always consider edge cases, "
                  "performance constraints, and user experience requirements.",
        tools=[analyze_tech_landscape],
        verbose=True,
        allow_delegation=False
    )


def create_architect_agent():
    """Create the Software Architect agent."""
    return Agent(
        role="Software Architect",
        goal="Design a scalable, fault-tolerant system architecture for the "
             "collaborative document editing platform based on the requirements.",
        backstory="You are a principal software architect with expertise in distributed systems, "
                  "real-time data synchronization, and cloud-native architecture. You have "
                  "designed systems handling millions of concurrent users at companies like "
                  "Google, Notion, and Figma. You favor pragmatic architecture choices that "
                  "balance complexity with scalability.",
        tools=[analyze_tech_landscape],
        verbose=True,
        allow_delegation=False
    )


def create_implementation_agent():
    """Create the Implementation Planner agent."""
    return Agent(
        role="Implementation Planner",
        goal="Create a detailed implementation plan with phases, milestones, "
             "team structure, and delivery strategy for the architecture.",
        backstory="You are a senior engineering manager who has delivered multiple "
                  "large-scale software projects on time. You understand how to break down "
                  "complex architectures into manageable sprints, allocate resources efficiently, "
                  "and set up effective CI/CD pipelines. You balance speed with quality.",
        tools=[analyze_tech_landscape],
        verbose=True,
        allow_delegation=False
    )


def create_risk_agent():
    """Create the Risk Assessment agent."""
    return Agent(
        role="Risk Analyst",
        goal="Identify and assess technical and project risks, providing "
             "concrete mitigation strategies for the architecture design.",
        backstory="You are a risk management specialist who has seen many software "
                  "projects succeed and fail. You have a keen eye for identifying technical "
                  "debt, scalability bottlenecks, and organizational risks before they "
                  "become critical. You always provide actionable mitigation plans.",
        tools=[evaluate_architecture_risks],
        verbose=True,
        allow_delegation=False
    )


# ============================================================================
# TASK DEFINITIONS
# ============================================================================

def create_requirements_task(requirements_agent):
    """Define the requirements gathering task."""
    return Task(
        description="Analyze and define comprehensive requirements for a real-time collaborative "
                   "document editing platform (similar to Google Docs). Use the technology "
                   "landscape tool to understand current capabilities. Define: "
                   "1) 5-6 key functional requirements with acceptance criteria, "
                   "2) 3-4 non-functional requirements (performance, scalability, security), "
                   "3) Target users and primary use cases, "
                   "4) Integration points with external systems (SSO, storage, email). "
                   "The system must support 10 million concurrent users.",
        agent=requirements_agent,
        expected_output="A structured requirements document with functional requirements, "
                       "non-functional requirements, user personas, use cases, and "
                       "integration specifications for a collaborative editing platform"
    )


def create_architecture_task(architect_agent):
    """Define the architecture design task."""
    return Task(
        description="Based on the requirements defined by the Requirements Analyst, design "
                   "a high-level system architecture for the collaborative editing platform. "
                   "Use the technology landscape tool to evaluate options. Include: "
                   "1) Architecture pattern selection (microservices, event-driven, etc.), "
                   "2) Major components/services with responsibilities, "
                   "3) Data flow and communication patterns, "
                   "4) Technology stack recommendations (languages, frameworks, databases), "
                   "5) Scalability strategy to handle 10M concurrent users.",
        agent=architect_agent,
        expected_output="A detailed architecture design document including component diagram, "
                       "technology selections, data flow patterns, and scalability strategy "
                       "for the collaborative editing platform"
    )


def create_implementation_task(implementation_agent):
    """Define the implementation planning task."""
    return Task(
        description="Based on the system architecture designed by the Architect, create a "
                   "comprehensive implementation plan. Include: "
                   "1) Development phases with milestones (Phase 1: MVP, Phase 2: Scale, Phase 3: Polish), "
                   "2) Team structure and required skills, "
                   "3) CI/CD pipeline design, "
                   "4) Testing strategy (unit, integration, E2E, load testing), "
                   "5) Estimated timeline for each phase.",
        agent=implementation_agent,
        expected_output="A detailed implementation plan with phased delivery milestones, "
                       "team organization, CI/CD strategy, testing approach, and timeline "
                       "estimates for building the collaborative editing platform"
    )


def create_risk_task(risk_agent):
    """Define the risk assessment task."""
    return Task(
        description="Based on the architecture design and implementation plan, perform a "
                   "comprehensive risk assessment. Use the risk evaluation tool to analyze "
                   "common risks. Include: "
                   "1) Identify 4-5 key technical risks with likelihood and impact ratings, "
                   "2) Assess organizational and project management risks, "
                   "3) Propose specific mitigation strategies for each risk, "
                   "4) Identify potential architectural bottlenecks, "
                   "5) Provide overall recommendations for project success.",
        agent=risk_agent,
        expected_output="A risk assessment report with identified risks, impact analysis, "
                       "mitigation strategies, and strategic recommendations for the "
                       "collaborative editing platform project"
    )


# ============================================================================
# CREW ORCHESTRATION
# ============================================================================

def main():
    """
    Main function to orchestrate the architecture design crew.
    """
    print("=" * 80)
    print("CrewAI Multi-Agent Software Architecture Design System")
    print("Designing a Real-Time Collaborative Document Editor")
    print("=" * 80)
    print()
    print("🏗️  Project: Real-time Collaborative Document Editor")
    print("🎯 Target: 10 million concurrent users")
    print("📐 Approach: Sequential task-based architecture design")
    print()

    # Validate configuration before proceeding
    print("🔍 Validating configuration...")
    if not validate_config():
        print("❌ Configuration validation failed. Please set up your .env file.")
        exit(1)

    # Set environment variables for CrewAI
    os.environ["OPENAI_API_KEY"] = Config.API_KEY
    os.environ["OPENAI_API_BASE"] = Config.API_BASE

    if Config.USE_GROQ:
        os.environ["OPENAI_MODEL_NAME"] = Config.OPENAI_MODEL

    print("✅ Configuration validated successfully!")
    print()
    Config.print_summary()
    print()

    # Create agents
    print("[1/4] Creating Requirements Analyst Agent...")
    requirements_agent = create_requirements_agent()

    print("[2/4] Creating Software Architect Agent...")
    architect_agent = create_architect_agent()

    print("[3/4] Creating Implementation Planner Agent...")
    implementation_agent = create_implementation_agent()

    print("[4/4] Creating Risk Analyst Agent...")
    risk_agent = create_risk_agent()

    print("\n✅ All agents created successfully!")
    print()

    # Create tasks
    print("Creating tasks for the crew...")
    requirements_task = create_requirements_task(requirements_agent)
    architecture_task = create_architecture_task(architect_agent)
    implementation_task = create_implementation_task(implementation_agent)
    risk_task = create_risk_task(risk_agent)

    print("Tasks created successfully!")
    print()

    # Create the crew with sequential task execution
    print("Forming the Architecture Design Crew...")
    print("Task Sequence: RequirementsAgent → ArchitectAgent → ImplementationAgent → RiskAgent")
    print()

    crew = Crew(
        agents=[requirements_agent, architect_agent, implementation_agent, risk_agent],
        tasks=[requirements_task, architecture_task, implementation_task, risk_task],
        verbose=True,
        process="sequential"
    )

    # Execute the crew
    print("=" * 80)
    print("Starting Crew Execution...")
    print("Designing architecture for Real-Time Collaborative Document Editor")
    print("=" * 80)
    print()

    try:
        result = crew.kickoff()

        print()
        print("=" * 80)
        print("✅ Crew Execution Completed Successfully!")
        print("=" * 80)
        print()
        print("FINAL ARCHITECTURE DESIGN REPORT:")
        print("-" * 80)
        print(result)
        print("-" * 80)

        # Save output to file
        output_filename = "crewai_architecture_output.txt"
        output_path = Path(__file__).parent / output_filename

        with open(output_path, "w") as f:
            f.write("=" * 80 + "\n")
            f.write("CrewAI Multi-Agent Software Architecture Design Report\n")
            f.write("Real-Time Collaborative Document Editor\n")
            f.write("=" * 80 + "\n\n")
            f.write(f"Execution Time: {datetime.now()}\n")
            f.write(f"API Version: OpenAI ({Config.OPENAI_MODEL})\n\n")
            f.write("FINAL ARCHITECTURE DESIGN REPORT:\n")
            f.write("-" * 80 + "\n")
            f.write(str(result))
            f.write("\n" + "-" * 80 + "\n")

        print(f"\n✅ Output saved to {output_filename}")

        # Print educational comparison
        print("\n" + "-" * 80)
        print("EDUCATIONAL NOTE: CrewAI vs AutoGen for Architecture Design")
        print("-" * 80)
        print("""
This workflow demonstrated CrewAI's TASK-BASED approach to architecture design:
- Each agent had a specific, well-defined task with expected output
- Tasks were executed SEQUENTIALLY (Requirements → Architecture → Implementation → Risk)
- Each agent worked independently on their task
- Output from earlier tasks was available as context for later tasks

Key observation: The sequential approach ensures each phase is completed before the
next begins. This provides structure but limits cross-pollination of ideas between
agents that AutoGen's GroupChat naturally enables.
""")

    except Exception as e:
        print(f"\n❌ Error during crew execution: {str(e)}")
        print("\n🔍 Troubleshooting:")
        print("   1. Verify OPENAI_API_KEY is set")
        print("   2. Check API key has sufficient credits")
        print("   3. Verify internet connection")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()
