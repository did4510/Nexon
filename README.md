# Nexon Support System

A powerful and aesthetic Discord ticket bot with advanced features, AI integration, and comprehensive staff management capabilities.

## Features

### Core Functionality
- **Advanced Ticket Management**
  - Category-based ticket creation
  - Custom forms per category
  - Anonymous ticket option
  - Automatic ticket numbering
  - Ticket transcripts and logging
  - Customizable ticket statuses
  - Internal notes system
  - Ticket linking
  - Scheduled follow-ups

### Staff Management
- **Performance Tracking**
  - Response time metrics
  - Resolution time tracking
  - Satisfaction scores
  - Staff activity monitoring
  - Performance analytics
  - Shift management
  - Specialization tracking

### AI Integration
- **Smart Features**
  - Sentiment analysis
  - Automatic categorization
  - Missing information detection
  - Ticket summarization
  - Keyword extraction
  - Priority analysis
  - Response suggestions

### Knowledge Base
- **Article Management**
  - Category organization
  - Search functionality
  - Automatic suggestions
  - Usage tracking
  - Feedback system
  - Related articles
  - Version history

### Macro System
- **Quick Responses**
  - Category-specific macros
  - Usage tracking
  - Keyword-based suggestions
  - Permission management
  - Dynamic placeholders
  - Statistics tracking

### SLA Monitoring
- **Service Level Agreements**
  - Response time tracking
  - Resolution time tracking
  - Automatic escalation
  - Warning notifications
  - SLA breach tracking
  - Custom SLA per category
  - Performance reporting

### User Interface
- **Aesthetic Design**
  - Custom embeds
  - Interactive buttons
  - Dynamic forms
  - Status indicators
  - Progress tracking
  - Theme customization
  - Mobile-friendly layout

## Installation

1. Clone the repository:
```bash
git clone https://github.com/did4510/Nexon.git
cd nexon
```

2. Create a virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # Linux/Mac
venv\Scripts\activate     # Windows
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Create a `.env` file with your configuration:
```env
DISCORD_TOKEN=your_bot_token
APPLICATION_ID=your_application_id
OPENAI_API_KEY=your_openai_key  # Optional, for AI features
```

5. Initialize the database:
```bash
alembic upgrade head
```

6. Start the bot:
```bash
python main.py
```

## Configuration

### Initial Setup
1. Invite the bot to your server with required permissions
2. Use `/config setup` to initialize server settings
3. Configure ticket categories and staff roles
4. Set up SLA rules and escalation channels
5. Customize bot appearance and behavior

### Available Settings
- Ticket parent category
- Log channels
- Staff roles
- Theme colors
- Language preferences
- SLA configuration
- Auto-close settings
- AI feature toggles

## Commands

### Ticket Management
- `/ticket create` - Create a new ticket
- `/ticket close` - Close a ticket
- `/ticket claim` - Claim a ticket
- `/ticket transfer` - Transfer to another staff member
- `/ticket note` - Add internal note
- `/ticket link` - Link related tickets
- `/ticket followup` - Schedule follow-up

### Staff Commands
- `/staff stats` - View performance stats
- `/staff duty` - Toggle duty status
- `/staff schedule` - Manage shifts
- `/staff report` - Generate performance report

### Knowledge Base
- `/kb create` - Create new article
- `/kb search` - Search articles
- `/kb edit` - Edit article
- `/kb delete` - Delete article
- `/kb suggest` - Get article suggestions

### Macros
- `/macro create` - Create new macro
- `/macro use` - Use a macro
- `/macro list` - List available macros
- `/macro stats` - View usage statistics

### Configuration
- `/config setup` - Initial setup
- `/config edit` - Edit settings
- `/config view` - View current settings
- `/config backup` - Backup settings

## Contributing

1. Fork the repository
2. Create a feature branch
3. Commit your changes
4. Push to the branch
5. Create a Pull Request

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Support

For support, join our [Discord server](https://discord.gg/) or open an issue on GitHub.
