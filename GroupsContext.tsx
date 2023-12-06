// GroupsContext.tsx
import React, { createContext, useState } from 'react';
import { Group } from './types';

interface GroupsContextProps {
  groups: Group[];
  addGroup: (group: Group) => void;
  updateGroup: (group: Group) => void;
  deleteGroup: (groupId: string) => void;
}

const initialState: Group[] = JSON.parse(localStorage.getItem('groups') || '[]');

export const GroupsContext = createContext<GroupsContextProps>({
  groups: initialState,
  addGroup: () => {},
  updateGroup: () => {},
  deleteGroup: () => {}
});

export const GroupsProvider: React.FC = ({ children }) => {
  const [groups, setGroups] = useState<Group[]>(initialState);

  const saveGroups = (groups: Group[]) => {
    localStorage.setItem('groups', JSON.stringify(groups));
    setGroups(groups);
  };

  const addGroup = (newGroup: Group) => {
    saveGroups([...groups, newGroup]);
  };

  const updateGroup = (updatedGroup: Group) => {
    const updatedGroups = groups.map(group => group.id === updatedGroup.id ? updatedGroup : group);
    saveGroups(updatedGroups);
  };

  const deleteGroup = (groupId: string) => {
    const updatedGroups = groups.filter(group => group.id !== groupId);
    saveGroups(updatedGroups);
  };

  return (
    <GroupsContext.Provider value={{ groups, addGroup, updateGroup, deleteGroup }}>
      {children}
    </GroupsContext.Provider>
  );
};
