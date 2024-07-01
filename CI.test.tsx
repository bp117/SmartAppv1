// ChatInterface.test.tsx

import React from 'react';
import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import '@testing-library/jest-dom/extend-expect';
import ChatInterface from './ChatInterface';
import axios from 'axios';
import fetchMock from 'jest-fetch-mock';

jest.mock('axios');

beforeEach(() => {
  fetchMock.resetMocks();
});

describe('ChatInterface', () => {
  const defaultProps = {
    theme: 'dark',
    currentConversationId: null,
    setCurrentConversationId: jest.fn(),
    conversations: [],
    setConversations: jest.fn(),
    sidebarOpen: false,
    userSubGroups: '',
    userId: 'testUser'
  };

  test('renders correctly with initial state', () => {
    render(<ChatInterface {...defaultProps} />);
    expect(screen.getByText('Chat with Documents')).toBeInTheDocument();
  });

  test('updates input value', () => {
    render(<ChatInterface {...defaultProps} />);
    const input = screen.getByPlaceholderText('Type your message...');
    fireEvent.change(input, { target: { value: 'Hello' } });
    expect(input).toHaveValue('Hello');
  });

  test('fetches and sets prompts correctly', async () => {
    fetchMock.mockResponseOnce(JSON.stringify({ prompt_templates: [{ id: '1', status: 'approved' }] }));

    render(<ChatInterface {...defaultProps} />);
    expect(fetchMock).toHaveBeenCalledWith(expect.stringContaining('/usecase_prompt_templates/'));

    await waitFor(() => expect(screen.getByText('approved')).toBeInTheDocument());
  });

  test('selecting a prompt updates the state', () => {
    render(<ChatInterface {...defaultProps} />);
    const select = screen.getByTestId('prompt-select');
    fireEvent.change(select, { target: { value: '1' } });
    expect(select).toHaveValue('1');
  });

  test('sending a message works correctly', async () => {
    fetchMock.mockResponseOnce(JSON.stringify({ result: 'Hello from bot' }));

    render(<ChatInterface {...defaultProps} />);
    const sendButton = screen.getByText('Send');
    fireEvent.click(sendButton);

    await waitFor(() => expect(screen.getByText('Hello from bot')).toBeInTheDocument());
  });

  test('file upload works correctly', async () => {
    axios.post.mockResolvedValue({ data: { requestId: '123' } });

    render(<ChatInterface {...defaultProps} />);
    const fileInput = screen.getByTestId('file-input');
    const file = new File(['hello'], 'hello.png', { type: 'image/png' });
    fireEvent.change(fileInput, { target: { files: [file] } });

    await waitFor(() => expect(axios.post).toHaveBeenCalledWith(expect.stringContaining('UPLOAD_ENDPOINT')));
  });

  test('fetching bot response works correctly', async () => {
    fetchMock.mockResponseOnce(JSON.stringify({ result: 'Bot response' }));

    render(<ChatInterface {...defaultProps} />);
    const sendButton = screen.getByText('Send');
    fireEvent.click(sendButton);

    await waitFor(() => expect(screen.getByText('Bot response')).toBeInTheDocument());
  });

  test('toggles sidebar', () => {
    render(<ChatInterface {...defaultProps} />);
    const toggleButton = screen.getByTestId('sidebar-toggle');
    fireEvent.click(toggleButton);
    expect(defaultProps.setSidebarOpen).toHaveBeenCalledWith(true);
  });

  test('handles prompt variables correctly', () => {
    render(<ChatInterface {...defaultProps} />);
    const prompt = { id: '1', template: 'Hello {{name}}' };
    const select = screen.getByTestId('prompt-select');
    fireEvent.change(select, { target: { value: prompt.id } });
    expect(screen.getByText('Hello {{name}}')).toBeInTheDocument();
  });

  test('handles errors correctly', async () => {
    fetchMock.mockReject(new Error('API error'));

    render(<ChatInterface {...defaultProps} />);
    const sendButton = screen.getByText('Send');
    fireEvent.click(sendButton);

    await waitFor(() => expect(screen.getByText('Error fetching bot response')).toBeInTheDocument());
  });

  test('selecting environment type updates the state', () => {
    render(<ChatInterface {...defaultProps} />);
    const environmentSelect = screen.getByTestId('environment-select');
    fireEvent.change(environmentSelect, { target: { value: 'gcp' } });
    expect(environmentSelect).toHaveValue('gcp');
  });

  test('component cleans up correctly on unmount', () => {
    const { unmount } = render(<ChatInterface {...defaultProps} />);
    unmount();
    // Check for any cleanup tasks if needed
  });

  test('fetching usecases works correctly', async () => {
    fetchMock.mockResponseOnce(JSON.stringify({ usecases: [{ id: '1', status: 'approved' }] }));

    render(<ChatInterface {...defaultProps} />);
    await waitFor(() => expect(screen.getByText('approved')).toBeInTheDocument());
  });

  test('applies styles correctly based on theme', () => {
    render(<ChatInterface {...defaultProps} />);
    const label = screen.getByText('Chat with Documents');
    expect(label).toHaveStyle('color: #fff');
  });
});
