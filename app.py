"""Streamlit UI for Natural Language Agent Builder."""
import streamlit as st
import json
from pathlib import Path

from src.agent_generator import AgentGenerator
from src.blocks import BlockManager
from src.templates import TemplateManager
from src.config import validate_config, GENERATED_AGENTS_DIR

# Page configuration
st.set_page_config(
    page_title="Natural Language Agent Builder",
    page_icon="🧠",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS
st.markdown("""
<style>
    .main-header {
        font-size: 3rem;
        font-weight: 700;
        color: #1f77b4;
        text-align: center;
        margin-bottom: 1rem;
    }
    .sub-header {
        font-size: 1.2rem;
        color: #666;
        text-align: center;
        margin-bottom: 2rem;
    }
    .success-box {
        padding: 1rem;
        background-color: #d4edda;
        border-left: 4px solid #28a745;
        margin: 1rem 0;
    }
    .info-box {
        padding: 1rem;
        background-color: #d1ecf1;
        border-left: 4px solid #17a2b8;
        margin: 1rem 0;
    }
    .warning-box {
        padding: 1rem;
        background-color: #fff3cd;
        border-left: 4px solid #ffc107;
        margin: 1rem 0;
    }
</style>
""", unsafe_allow_html=True)


def initialize_session_state():
    """Initialize session state variables."""
    if 'generated_agent' not in st.session_state:
        st.session_state.generated_agent = None
    if 'agent_history' not in st.session_state:
        st.session_state.agent_history = []


def main():
    """Main application function."""
    initialize_session_state()
    
    # Header
    st.markdown('<div class="main-header">🧠 Natural Language Agent Builder</div>', unsafe_allow_html=True)
    st.markdown('<div class="sub-header">Build powerful AI agents using plain language — no code required</div>', unsafe_allow_html=True)
    
    # Check configuration
    try:
        validate_config()
    except ValueError as e:
        st.error(f"⚠️ Configuration Error: {e}")
        st.info("Please copy `.env.example` to `.env` and fill in your API keys.")
        return
    
    # Initialize managers
    try:
        generator = AgentGenerator()
        block_manager = BlockManager()
        template_manager = TemplateManager()
    except Exception as e:
        st.error(f"Failed to initialize: {e}")
        return
    
    # Sidebar
    with st.sidebar:
        st.header("⚙️ Options")
        
        creation_mode = st.radio(
            "Creation Mode",
            ["Natural Language", "From Template", "View Generated"],
            help="Choose how you want to create your agent"
        )
        
        st.divider()
        
        # Show available blocks
        with st.expander("📦 Available Tools/Blocks"):
            blocks = block_manager.get_all_blocks()
            for block in blocks:
                st.markdown(f"**{block.name}**")
                st.caption(block.description)
                st.caption(f"Category: {block.category}")
                st.divider()
        
        # Show templates
        with st.expander("📋 Templates"):
            templates = template_manager.get_all_templates()
            for template in templates:
                st.markdown(f"**{template.name}**")
                st.caption(template.description)
                st.divider()
    
    # Main content based on mode
    if creation_mode == "Natural Language":
        show_natural_language_mode(generator)
    elif creation_mode == "From Template":
        show_template_mode(generator, template_manager)
    else:
        show_generated_agents_mode()


def show_natural_language_mode(generator):
    """Show the natural language agent creation interface."""
    st.header("✨ Describe Your Agent")
    
    # Examples
    with st.expander("💡 Example Descriptions"):
        st.markdown("""
        - *"Create an agent that finds LinkedIn profiles, enriches them with emails, and drafts personalized cold emails"*
        - *"Build an agent that tracks competitor news, summarizes insights, and stores them in Notion"*
        - *"I need an agent to generate social media posts and schedule them on LinkedIn and Twitter"*
        - *"Create an agent that analyzes customer feedback and generates sentiment reports"*
        """)
    
    # Input
    user_description = st.text_area(
        "Describe what you want your agent to do:",
        height=150,
        placeholder="E.g., 'Create an agent that monitors social media mentions, analyzes sentiment, and sends alerts for negative feedback...'"
    )
    
    col1, col2, col3 = st.columns([1, 1, 2])
    
    with col1:
        generate_btn = st.button("🚀 Generate Agent", type="primary", use_container_width=True)
    
    with col2:
        if st.session_state.generated_agent:
            refine_mode = st.checkbox("🔧 Refine Mode")
        else:
            refine_mode = False
    
    # Generate or refine
    if generate_btn and user_description:
        with st.spinner("🤖 Generating your agent..."):
            try:
                if refine_mode and st.session_state.generated_agent:
                    result = generator.refine_agent(
                        st.session_state.generated_agent['agent'],
                        user_description
                    )
                    st.success("✅ Agent refined successfully!")
                else:
                    result = generator.generate_from_description(user_description)
                    st.success("✅ Agent generated successfully!")
                
                st.session_state.generated_agent = result
                st.session_state.agent_history.append(result)
                
            except Exception as e:
                st.error(f"❌ Error generating agent: {e}")
                return
    
    # Display generated agent
    if st.session_state.generated_agent:
        st.divider()
        display_agent(st.session_state.generated_agent, generator)


def show_template_mode(generator, template_manager):
    """Show the template-based agent creation interface."""
    st.header("📋 Create from Template")
    
    templates = template_manager.get_all_templates()
    
    # Template selection
    template_options = {t.name: t.id for t in templates}
    selected_template_name = st.selectbox(
        "Choose a template:",
        options=list(template_options.keys())
    )
    
    template_id = template_options[selected_template_name]
    template = template_manager.get_template_by_id(template_id)
    
    # Show template details
    st.info(f"📝 {template.description}")
    
    with st.expander("🔍 View Template Details"):
        st.json(template.agent_config)
    
    # Generate from template
    if st.button("🚀 Use This Template", type="primary"):
        try:
            result = generator.generate_from_template(template_id)
            st.session_state.generated_agent = result
            st.success("✅ Agent created from template!")
        except Exception as e:
            st.error(f"❌ Error: {e}")
            return
    
    # Display generated agent
    if st.session_state.generated_agent:
        st.divider()
        display_agent(st.session_state.generated_agent, generator)


def show_generated_agents_mode():
    """Show previously generated agents."""
    st.header("📁 Generated Agents")
    
    # List saved agents
    agent_files = list(GENERATED_AGENTS_DIR.glob("*.json"))
    
    if not agent_files:
        st.info("No generated agents found yet. Create your first agent!")
        return
    
    # Sort by modification time (newest first)
    agent_files.sort(key=lambda x: x.stat().st_mtime, reverse=True)
    
    st.write(f"Found {len(agent_files)} saved agents:")
    
    for agent_file in agent_files:
        with st.expander(f"📄 {agent_file.stem}"):
            try:
                with open(agent_file, 'r') as f:
                    agent_data = json.load(f)
                
                # Show metadata
                if 'metadata' in agent_data:
                    metadata = agent_data['metadata']
                    st.caption(f"Generated: {metadata.get('generated_at', 'Unknown')}")
                    if 'description' in metadata:
                        st.caption(f"Description: {metadata['description']}")
                
                # Show agent config
                st.json(agent_data['agent'])
                
                # Actions
                col1, col2 = st.columns(2)
                with col1:
                    if st.button(f"Load into Editor", key=f"load_{agent_file.stem}"):
                        st.session_state.generated_agent = agent_data
                        st.success("Agent loaded! Switch to 'Natural Language' mode to edit.")
                
                with col2:
                    # Download button
                    st.download_button(
                        label="Download JSON",
                        data=json.dumps(agent_data, indent=2),
                        file_name=agent_file.name,
                        mime="application/json",
                        key=f"download_{agent_file.stem}"
                    )
                
            except Exception as e:
                st.error(f"Error loading agent: {e}")


def display_agent(agent_data, generator):
    """Display the generated agent with validation and export options."""
    agent_config = agent_data.get('agent', {})
    
    st.subheader("🎯 Generated Agent")
    
    # Basic info
    col1, col2 = st.columns(2)
    with col1:
        st.markdown(f"**Name:** {agent_config.get('name', 'Unknown')}")
    with col2:
        st.markdown(f"**Tasks:** {len(agent_config.get('tasks', []))}")
    
    st.markdown(f"**Description:** {agent_config.get('description', 'N/A')}")
    
    # Tabs for different views
    tab1, tab2, tab3, tab4 = st.tabs(["📋 Overview", "🔧 Tasks", "💬 System Prompt", "📄 Full JSON"])
    
    with tab1:
        # Validation
        issues = generator.validate_agent(agent_config)
        if issues:
            st.warning("⚠️ Validation Issues:")
            for issue in issues:
                st.markdown(f"- {issue}")
        else:
            st.success("✅ Agent configuration is valid!")
        
        # Memory configuration
        memory = agent_config.get('memory', {})
        if memory.get('enabled'):
            st.info(f"🧠 Memory Enabled: {', '.join(memory.get('keys', []))}")
    
    with tab2:
        # Display tasks
        for i, task in enumerate(agent_config.get('tasks', []), 1):
            with st.container():
                st.markdown(f"### Task {i}: {task.get('name')}")
                st.markdown(f"**Block:** `{task.get('blockName')}`")
                st.markdown("**Inputs:**")
                st.json(task.get('inputs', {}))
                st.divider()
    
    with tab3:
        # System prompt
        st.text_area(
            "System Prompt",
            value=agent_config.get('systemPrompt', ''),
            height=300,
            disabled=True
        )
    
    with tab4:
        # Full JSON
        st.json(agent_config)
    
    # Actions
    st.divider()
    col1, col2, col3 = st.columns(3)
    
    with col1:
        if st.button("💾 Save Agent", type="primary", use_container_width=True):
            try:
                filepath = generator.save_agent(agent_data)
                st.success(f"✅ Saved to: {filepath.name}")
            except Exception as e:
                st.error(f"❌ Error saving: {e}")
    
    with col2:
        # Download button
        st.download_button(
            label="📥 Download JSON",
            data=json.dumps(agent_data, indent=2),
            file_name=f"{agent_config.get('name', 'agent').lower().replace(' ', '_')}.json",
            mime="application/json",
            use_container_width=True
        )
    
    with col3:
        if st.button("🗑️ Clear", use_container_width=True):
            st.session_state.generated_agent = None
            st.rerun()


if __name__ == "__main__":
    main()

