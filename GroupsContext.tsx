import React, { createContext, useState } from 'react';
import { Group } from './types';

interface GroupsContextProps {
  groups: Group[];
  setGroups: React.Dispatch<React.SetStateAction<Group[]>>;
}

export const GroupsContext = createContext<GroupsContextProps>({
  groups: [],
  setGroups: () => {},
});

export const GroupsProvider: React.FC = ({ children }) => {
  const [groups, setGroups] = useState<Group[]>([]);

  return (
    <GroupsContext.Provider value={{ groups, setGroups }}>
      {children}
    </GroupsContext.Provider>
  );
};
