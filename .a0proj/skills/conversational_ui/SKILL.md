# Conversational UI Design Skill

## Overview
Design and implement modern conversational chat interfaces for customer interactions.

## UI Components

### Chat Container
```tsx
<ChatContainer>
  <ChatHeader />
  <MessageList messages={messages} />
  <ChatInput onSend={handleSend} />
</ChatContainer>
```

### Message Types
- Text messages
- Quick action buttons
- Service cards
- Appointment cards
- Image attachments

### Quick Actions
```tsx
<QuickActions>
  <ActionButton label="Book Appointment" action="book" />
  <ActionButton label="View Services" action="services" />
  <ActionButton label="My Bookings" action="bookings" />
</QuickActions>
```

### Service Card
```tsx
<ServiceCard
  name="Men's Haircut"
  price={170}
  duration={30}
  onSelect={handleSelect}
/>
```

## Interaction Patterns

1. **Natural Language Input**: Free-form text understanding
2. **Guided Flows**: Step-by-step booking wizard
3. **Quick Replies**: Pre-defined response options
4. **Rich Cards**: Visual service/appointment displays

## Animation
- Smooth message appearance
- Typing indicators
- Loading states
- Transition effects
