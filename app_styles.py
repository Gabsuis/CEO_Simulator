BASE_CSS = """
<style>
    /* Hide default multipage sidebar nav (we render our own top tabs) */
    [data-testid="stSidebarNav"] {
        display: none !important;
    }

    .header {
        text-align: center;
        padding: 20px;
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        border-radius: 10px;
        margin-bottom: 20px;
    }
    .agent-badge {
        display: inline-block;
        padding: 8px 16px;
        border-radius: 20px;
        background: #667eea;
        color: white;
        font-weight: bold;
        margin: 5px 5px 5px 0;
    }
    /* Floating session dashboard */
    .floating-dashboard {
        position: fixed;
        top: 20px;
        left: 20px;
        background: rgba(255, 255, 255, 0.95);
        backdrop-filter: blur(10px);
        border: 1px solid rgba(102, 126, 234, 0.2);
        border-radius: 12px;
        padding: 12px 16px;
        box-shadow: 0 4px 20px rgba(0,0,0,0.1);
        z-index: 1000;
        font-size: 12px;
        min-width: 200px;
    }
    .floating-dashboard h4 {
        margin: 0 0 8px 0;
        font-size: 14px;
        color: #667eea;
    }
    .floating-dashboard .metric-row {
        display: flex;
        justify-content: space-between;
        margin-bottom: 4px;
        font-size: 11px;
    }
    .floating-dashboard .metric-label {
        color: #666;
    }
    .floating-dashboard .metric-value {
        color: #333;
        font-weight: bold;
    }

    /* Enhanced Message Styling */
    .chat-message {
        padding: 16px;
        border-radius: 12px;
        margin: 12px 0;
        box-shadow: 0 2px 8px rgba(0,0,0,0.1);
        transition: all 0.3s ease;
    }
    .chat-message:hover {
        box-shadow: 0 4px 16px rgba(0,0,0,0.15);
    }
    .message-user {
        background: linear-gradient(135deg, #e3f2fd 0%, #bbdefb 100%);
        border-left: 4px solid #2196F3;
        margin-left: 20px;
        margin-right: 60px;
    }
    .message-assistant {
        background: linear-gradient(135deg, #f5f5f5 0%, #eeeeee 100%);
        border-left: 4px solid #667eea;
        margin-right: 20px;
        margin-left: 60px;
    }
    .message-system {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        text-align: center;
        margin: 16px auto;
        max-width: 280px;
        font-size: 14px;
        font-weight: 500;
        border: none;
        box-shadow: 0 2px 12px rgba(102, 126, 234, 0.4);
        animation: fadeIn 0.5s ease-in;
    }
    @keyframes fadeIn {
        from { opacity: 0; transform: translateY(-10px); }
        to { opacity: 1; transform: translateY(0); }
    }

    /* Avatar Styling */
    .agent-avatar {
        width: 48px;
        height: 48px;
        border-radius: 50%;
        margin-right: 16px;
        border: 3px solid #667eea;
        object-fit: cover;
        box-shadow: 0 2px 8px rgba(0,0,0,0.2);
        transition: all 0.3s ease;
    }
    .agent-avatar:hover {
        transform: scale(1.05);
        box-shadow: 0 4px 16px rgba(0,0,0,0.3);
    }

    /* Typing Indicator */
    .message-typing {
        animation: typing 1.5s infinite;
        display: inline-block;
    }
    @keyframes typing {
        0%, 60%, 100% { opacity: 1; }
        30% { opacity: 0.3; }
    }

    /* Dream UI Elements */
    .dream-card {
        background: linear-gradient(135deg, #ffffff 0%, #f8f9fa 100%);
        border-radius: 16px;
        padding: 20px;
        margin: 12px 0;
        box-shadow: 0 4px 20px rgba(0,0,0,0.1);
        border: 1px solid rgba(102, 126, 234, 0.1);
    }
    .dream-header {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        padding: 24px;
        border-radius: 16px;
        margin-bottom: 24px;
        text-align: center;
    }
    .character-grid {
        display: grid;
        grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
        gap: 16px;
        margin: 20px 0;
    }
    .character-card {
        background: white;
        padding: 16px;
        border-radius: 12px;
        box-shadow: 0 2px 12px rgba(0,0,0,0.1);
        text-align: center;
        transition: all 0.3s ease;
        border: 2px solid transparent;
    }
    .character-card:hover {
        transform: translateY(-4px);
        box-shadow: 0 8px 24px rgba(0,0,0,0.15);
    }
    .character-card.selected {
        border-color: #667eea;
        background: linear-gradient(135deg, #f8f9ff 0%, #ffffff 100%);
    }

    /* Meeting Panel Styling */
    .meeting-panel {
        background: linear-gradient(135deg, #667eea10 0%, #764ba210 100%);
        border-radius: 16px;
        padding: 20px;
        margin: 16px 0;
    }
</style>
"""

