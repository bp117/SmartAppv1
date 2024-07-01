import { render, screen, fireEvent } from '@testing-library/react';
import ChatInterface from './ChatInterface';

const mockProps = {
  theme: 'light',
  currentConversationId: 1,
  setCurrentConversationId: jest.fn(),
  conversations: [
    {
      id: 1,
      title: 'Conversation 1',
      messages: [
        { role: 'user', content: 'Hello' },
        { role: 'bot', content: 'Hi there!' }
      ]
    }
  ],
  setConversations: jest.fn()
};

test('renders chat interface with initial state', () => {
  render(<ChatInterface {...mockProps} />);
  expect(screen.getByPlaceholderText('Type a message...')).toBeInTheDocument();
  expect(screen.getByText('Hi there!')).toBeInTheDocument();
});

test('updates input field on typing', () => {
  render(<ChatInterface {...mockProps} />);
  const inputField = screen.getByPlaceholderText('Type a message...');
  fireEvent.change(inputField, { target: { value: 'New message' } });
  expect(inputField.value).toBe('New message');
});

test('sends message on send button click', () => {
  render(<ChatInterface {...mockProps} />);
  const inputField = screen.getByPlaceholderText('Type a message...');
  fireEvent.change(inputField, { target: { value: 'New message' } });
  fireEvent.click(screen.getByRole('button', { name: /send/i }));
  expect(mockProps.setConversations).toHaveBeenCalled();
});

test('shows bot typing indicator when bot is typing', () => {
  render(<ChatInterface {...mockProps} />);
  fireEvent.click(screen.getByText('Send Message'));
  expect(screen.getByText('Bot is typing...')).toBeInTheDocument();
});

test('updates selected option', () => {
  render(<ChatInterface {...mockProps} />);
  const selectField = screen.getByRole('combobox');
  fireEvent.change(selectField, { target: { value: 'New option' } });
  expect(selectField.value).toBe('New option');
});
