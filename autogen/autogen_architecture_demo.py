"""
AutoGen GroupChat Demo - Software Architecture Design (Exercise 4)

This demonstrates AutoGen's conversational GroupChat approach applied to
a Software Architecture Design problem. Four specialist agents collaborate
in an emergent discussion to design a system architecture.

Agents:
1. RequirementsAgent - Gathers and analyzes system requirements
2. ArchitectAgent - Designs the system architecture
3. ImplementationAgent - Plans the implementation strategy
4. RiskAssessmentAgent - Evaluates risks and proposes mitigations
"""

import os
from datetime import datetime
from config import Config

# Try to import AutoGen
try:
    import autogen
except ImportError:
    print("ERROR: AutoGen is not installed!")
    print("Please run: pip install -r ../requirements.txt")
    exit(1)


class GroupChatArchitectureDesign:
    """Multi-agent GroupChat workflow for software architecture design using AutoGen"""

    def __init__(self):
        """Initialize the GroupChat with specialized agents"""
        if not Config.validate_setup():
            print("ERROR: Configuration validation failed!")
            exit(1)

        self.config_list = Config.get_config_list()
        self.llm_config = {"config_list": self.config_list, "temperature": Config.AGENT_TEMPERATURE}

        # Create agents and GroupChat
        self._create_agents()
        self._setup_groupchat()

        print("All AutoGen agents created and GroupChat initialized.")

    def _create_agents(self):
        """Create UserProxyAgent and 4 specialist AssistantAgents"""

        # UserProxyAgent acts as the tech lead who kicks off the discussion
        self.user_proxy = autogen.UserProxyAgent(
            name="TechLead",
            system_message="A tech lead who initiates the architecture design discussion and oversees the collaborative process.",
            human_input_mode="NEVER",
            code_execution_config=False,
            max_consecutive_auto_reply=0,
            is_termination_msg=lambda x: "TERMINATE" in x.get("content", ""),
        )

        # Requirements Agent - starts the conversation with requirements analysis
        self.requirements_agent = autogen.AssistantAgent(
            name="RequirementsAgent",
            system_message="""You are a senior requirements analyst specializing in software systems.
Your role in this group discussion is to START the conversation by analyzing and defining system requirements.

Your responsibilities:
- Define 5-6 key functional requirements for the system
- Identify 3-4 non-functional requirements (performance, scalability, security)
- Specify the target users and their primary use cases
- Identify integration points with external systems

When you present your findings, be specific with technical details and constraints.
After presenting your analysis, invite the ArchitectAgent to design the architecture.
Keep your response focused and under 400 words.""",
            llm_config=self.llm_config,
            description="A requirements analyst who gathers and defines functional and non-functional system requirements.",
        )

        # Architect Agent - designs the system architecture
        self.architect_agent = autogen.AssistantAgent(
            name="ArchitectAgent",
            system_message="""You are a senior software architect with expertise in distributed systems.
Your role in this group discussion is to DESIGN the system architecture based on requirements.

Your responsibilities:
- When the RequirementsAgent shares requirements, design a high-level system architecture
- Choose appropriate architecture patterns (microservices, event-driven, etc.)
- Define the major components/services and their interactions
- Select technology stack recommendations (languages, frameworks, databases)
- Include scalability and fault tolerance considerations

Reference specific requirements from the RequirementsAgent's analysis when making your design decisions.
After presenting your architecture, invite the ImplementationAgent to plan the implementation.
Keep your response focused and under 400 words.""",
            llm_config=self.llm_config,
            description="A software architect who designs system architecture, selects technology stacks, and defines component interactions.",
        )

        # Implementation Agent - plans the implementation strategy
        self.implementation_agent = autogen.AssistantAgent(
            name="ImplementationAgent",
            system_message="""You are a senior engineering manager specializing in software delivery.
Your role in this group discussion is to PLAN the implementation based on the architecture.

Your responsibilities:
- When the ArchitectAgent presents the architecture, create an implementation plan
- Define development phases with milestones and timelines
- Identify team structure and skill requirements
- Specify CI/CD pipeline and DevOps strategy
- Outline testing strategy (unit, integration, E2E)

Reference specific components from the ArchitectAgent and requirements from earlier discussion.
After presenting your plan, invite the RiskAssessmentAgent to evaluate risks.
Keep your response focused and under 400 words.""",
            llm_config=self.llm_config,
            description="An engineering manager who plans implementation phases, team structure, and delivery strategy.",
        )

        # Risk Assessment Agent - evaluates risks and concludes
        self.risk_agent = autogen.AssistantAgent(
            name="RiskAssessmentAgent",
            system_message="""You are a senior risk analyst specializing in software project risk management.
Your role in this group discussion is to EVALUATE risks and provide mitigation strategies.

Your responsibilities:
- When the ImplementationAgent presents the plan, identify 4-5 key technical and project risks
- Assess each risk's likelihood and impact (High/Medium/Low)
- Propose specific mitigation strategies for each risk
- Highlight any architectural decisions that could become bottlenecks
- Provide final recommendations for project success

Reference specific components from the architecture and implementation plan.
After your assessment, conclude the discussion by ending your message with the word TERMINATE.""",
            llm_config=self.llm_config,
            description="A risk analyst who evaluates project risks, assesses impact, and proposes mitigation strategies.",
        )

    def _setup_groupchat(self):
        """Create the GroupChat and GroupChatManager"""
        self.groupchat = autogen.GroupChat(
            agents=[
                self.user_proxy,
                self.requirements_agent,
                self.architect_agent,
                self.implementation_agent,
                self.risk_agent,
            ],
            messages=[],
            max_round=8,
            speaker_selection_method="auto",
            allow_repeat_speaker=False,
            send_introductions=True,
        )

        self.manager = autogen.GroupChatManager(
            groupchat=self.groupchat,
            llm_config=self.llm_config,
            is_termination_msg=lambda x: "TERMINATE" in x.get("content", ""),
        )

    def run(self):
        """Execute the GroupChat workflow"""
        print("\n" + "=" * 80)
        print("AUTOGEN GROUPCHAT - SOFTWARE ARCHITECTURE DESIGN")
        print("=" * 80)
        print(f"Start Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"Model: {Config.OPENAI_MODEL}")
        print(f"Max Rounds: {self.groupchat.max_round}")
        print(f"Speaker Selection: {self.groupchat.speaker_selection_method}")
        print("\nAgents in GroupChat:")
        for agent in self.groupchat.agents:
            print(f"  - {agent.name}")
        print("\n" + "=" * 80)
        print("MULTI-AGENT CONVERSATION BEGINS")
        print("=" * 80 + "\n")

        # Initiate the group chat conversation
        initial_message = """Team, we need to design the software architecture for a real-time collaborative
document editing platform (similar to Google Docs). The system must support:
- Real-time multi-user editing with conflict resolution
- Rich text formatting and media embedding
- Version history and document recovery
- Access control and sharing permissions
- Scalability to 10 million concurrent users

Let's collaborate on this:
1. RequirementsAgent: Start by defining the detailed requirements
2. ArchitectAgent: Design the system architecture
3. ImplementationAgent: Plan the implementation strategy
4. RiskAssessmentAgent: Evaluate risks and provide recommendations

RequirementsAgent, please begin with your requirements analysis."""

        chat_result = self.user_proxy.initiate_chat(
            self.manager,
            message=initial_message,
            summary_method="reflection_with_llm",
            summary_args={
                "summary_prompt": "Summarize the complete architecture design developed through this multi-agent discussion. Include: key requirements, architecture decisions, implementation plan, and risk assessment."
            },
        )

        # Print results
        self._print_summary(chat_result)

        # Save to file
        output_file = self._save_results(chat_result)
        print(f"\nFull results saved to: {output_file}")

        print(f"\nEnd Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print("=" * 80)

    def _print_summary(self, chat_result):
        """Print educational summary highlighting GroupChat behavior"""
        print("\n" + "=" * 80)
        print("CONVERSATION COMPLETE")
        print("=" * 80)

        print(f"\nTotal conversation rounds: {len(self.groupchat.messages)}")
        print("\nSpeaker order (as selected by GroupChatManager):")
        for i, msg in enumerate(self.groupchat.messages, 1):
            speaker = msg.get("name", "Unknown")
            content = msg.get("content", "")
            preview = content[:80].replace("\n", " ") + "..." if len(content) > 80 else content.replace("\n", " ")
            print(f"  {i}. [{speaker}]: {preview}")

        if chat_result.summary:
            print("\n" + "-" * 80)
            print("EXECUTIVE SUMMARY (LLM-generated reflection)")
            print("-" * 80)
            print(chat_result.summary)

        print("\n" + "-" * 80)
        print("EDUCATIONAL NOTE: AutoGen vs CrewAI for Architecture Design")
        print("-" * 80)
        print("""
This workflow demonstrated AutoGen's CONVERSATIONAL approach to software architecture:
- Agents were placed in a GroupChat and communicated naturally
- The GroupChatManager used LLM-based speaker selection (not hardcoded order)
- Agents referenced each other's contributions in their responses
- The conversation emerged organically through agent-to-agent interaction

Key observation: The architecture design benefited from the conversational approach
because architects could immediately respond to requirements, and risk analysts
could reference both architecture decisions and implementation plans in context.
""")

    def _save_results(self, chat_result):
        """Save GroupChat conversation and summary to file"""
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        output_dir = os.path.dirname(os.path.abspath(__file__))
        output_file = os.path.join(output_dir, f"architecture_groupchat_output_{timestamp}.txt")

        with open(output_file, 'w') as f:
            f.write("=" * 80 + "\n")
            f.write("AUTOGEN GROUPCHAT - SOFTWARE ARCHITECTURE DESIGN\n")
            f.write("=" * 80 + "\n")
            f.write(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
            f.write(f"Model: {Config.OPENAI_MODEL}\n")
            f.write(f"Conversation Rounds: {len(self.groupchat.messages)}\n\n")

            f.write("=" * 80 + "\n")
            f.write("MULTI-AGENT CONVERSATION\n")
            f.write("=" * 80 + "\n\n")

            for i, msg in enumerate(self.groupchat.messages, 1):
                speaker = msg.get("name", "Unknown")
                content = msg.get("content", "")
                f.write(f"--- Turn {i}: {speaker} ---\n")
                f.write(content + "\n\n")

            if chat_result.summary:
                f.write("=" * 80 + "\n")
                f.write("EXECUTIVE SUMMARY\n")
                f.write("=" * 80 + "\n")
                f.write(chat_result.summary + "\n")

        return output_file


if __name__ == "__main__":
    try:
        workflow = GroupChatArchitectureDesign()
        workflow.run()
        print("\nGroupChat workflow completed successfully!")
    except Exception as e:
        print(f"\nError during workflow execution: {str(e)}")
        print("\nTroubleshooting:")
        print("1. Verify API key is set in parent directory .env (../.env)")
        print("2. Check your API key has sufficient credits")
        print("3. Ensure pyautogen is installed: pip install -r ../requirements.txt")
        print("4. Verify internet connection")
        import traceback
        traceback.print_exc()
