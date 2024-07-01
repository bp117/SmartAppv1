import React from 'react';
import { render, screen, waitFor } from '@testing-library/react';
import '@testing-library/jest-dom/extend-expect';
import axios from 'axios';
import MockAdapter from 'axios-mock-adapter';
import { UserProvider, UserContext } from './UserContext';

// Create a new instance of axios-mock-adapter
const mock = new MockAdapter(axios);

describe('UserContext', () => {
  beforeEach(() => {
    mock.reset();
  });

  it('should initialize with default values', () => {
    render(
      <UserProvider>
        <UserContext.Consumer>
          {({ loggedInUser }) => (
            <div data-testid="loggedInUser">{loggedInUser ? loggedInUser.userName : 'No user'}</div>
          )}
        </UserContext.Consumer>
      </UserProvider>
    );

    expect(screen.getByTestId('loggedInUser')).toHaveTextContent('No user');
  });

  it('should fetch and set user data', async () => {
    const userInfoResponse = {
      user_name: 'Test User',
      user_id: '123',
      lan_id: 'testLanId',
      ad_iam_root_group_id: 1,
      ad_iam_sub_group_ids: [2, 3],
    };
    const userExistsResponse = {
      exists: true,
    };

    mock.onGet('/userinfo').reply(200, userInfoResponse);
    mock.onGet('/api/users/123').reply(200, userExistsResponse);

    render(
      <UserProvider>
        <UserContext.Consumer>
          {({ loggedInUser }) => (
            <div data-testid="loggedInUser">{loggedInUser ? loggedInUser.userName : 'No user'}</div>
          )}
        </UserContext.Consumer>
      </UserProvider>
    );

    await waitFor(() => expect(mock.history.get.length).toBe(2));
    await waitFor(() => expect(screen.getByTestId('loggedInUser')).toHaveTextContent('Test User'));
  });

  it('should save new user if they do not exist', async () => {
    const userInfoResponse = {
      user_name: 'New User',
      user_id: '124',
      lan_id: 'newLanId',
      ad_iam_root_group_id: 1,
      ad_iam_sub_group_ids: [2, 3],
    };
    const userExistsResponse = {
      exists: false,
    };

    mock.onGet('/userinfo').reply(200, userInfoResponse);
    mock.onGet('/api/users/124').reply(200, userExistsResponse);
    mock.onPost('/api/users').reply(200);

    render(
      <UserProvider>
        <UserContext.Consumer>
          {({ loggedInUser }) => (
            <div data-testid="loggedInUser">{loggedInUser ? loggedInUser.userName : 'No user'}</div>
          )}
        </UserContext.Consumer>
      </UserProvider>
    );

    await waitFor(() => expect(mock.history.get.length).toBe(2));
    await waitFor(() => expect(mock.history.post.length).toBe(1));
    await waitFor(() => expect(screen.getByTestId('loggedInUser')).toHaveTextContent('New User'));
  });
});
