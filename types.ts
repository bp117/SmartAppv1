export interface Group {
  id: string;
  name: string;
  parentId: string | null;
  subGroups?: Group[];
}
// types.ts
export interface Role {
  id: string;
  name: string;
  permissions: string[]; // Array of permission IDs
}

export interface Permission {
  id: string;
  name: string;
  description: string;
}
// RolesContext.tsx
import React, { createContext, useState } from 'react';
import { Role } from './types';

interface RolesContextProps {
  roles: Role[];
  addRole: (role: Role) => void;
  updateRole: (role: Role) => void;
  deleteRole: (roleId: string) => void;
}

const initialRoles: Role[] = JSON.parse(localStorage.getItem('roles') || '[]');

export const RolesContext = createContext<RolesContextProps>({
  roles: initialRoles,
  addRole: () => {},
  updateRole: () => {},
  deleteRole: () => {}
});

export const RolesProvider: React.FC = ({ children }) => {
  const [roles, setRoles] = useState<Role[]>(initialRoles);

  const saveRoles = (roles: Role[]) => {
    localStorage.setItem('roles', JSON.stringify(roles));
    setRoles(roles);
  };

  const addRole = (newRole: Role) => saveRoles([...roles, newRole]);

  const updateRole = (updatedRole: Role) => saveRoles(roles.map(role => role.id === updatedRole.id ? updatedRole : role));

  const deleteRole = (roleId: string) => saveRoles(roles.filter(role => role.id !== roleId));

  return (
    <RolesContext.Provider value={{ roles, addRole, updateRole, deleteRole }}>
      {children}
    </RolesContext.Provider>
  );
};
// PermissionsContext.tsx
import React, { createContext, useState } from 'react';
import { Permission } from './types';

interface PermissionsContextProps {
  permissions: Permission[];
  addPermission: (permission: Permission) => void;
  updatePermission: (permission: Permission) => void;
  deletePermission: (permissionId: string) => void;
}

const initialPermissions: Permission[] = JSON.parse(localStorage.getItem('permissions') || '[]');

export const PermissionsContext = createContext<PermissionsContextProps>({
  permissions: initialPermissions,
  addPermission: () => {},
  updatePermission: () => {},
  deletePermission: () => {}
});

export const PermissionsProvider: React.FC = ({ children }) => {
  const [permissions, setPermissions] = useState<Permission[]>(initialPermissions);

  const savePermissions = (permissions: Permission[]) => {
    localStorage.setItem('permissions', JSON.stringify(permissions));
    setPermissions(permissions);
  };

  const addPermission = (newPermission: Permission) => savePermissions([...permissions, newPermission]);

  const updatePermission = (updatedPermission: Permission) => savePermissions(permissions.map(permission => permission.id === updatedPermission.id ? updatedPermission : permission));

  const deletePermission = (permissionId: string) => savePermissions(permissions.filter(permission => permission.id !== permissionId));

  return (
    <PermissionsContext.Provider value={{ permissions, addPermission, updatePermission, deletePermission }}>
      {children}
    </PermissionsContext.Provider>
  );
};
import React, { useContext, useState } from 'react';
import { RolesContext } from './RolesContext';
import CommonGrid from './CommonGrid';
import { Button, Chip } from '@material-ui/core';
import RoleDialog from './RoleDialog';
import DeleteConfirmationDialog from './DeleteConfirmationDialog';
import { GridColDef } from '@material-ui/data-grid';

const RolesTab = () => {
  const { roles, addRole, updateRole, deleteRole } = useContext(RolesContext);
  const [isRoleDialogOpen, setIsRoleDialogOpen] = useState(false);
  const [isDeleteDialogOpen, setIsDeleteDialogOpen] = useState(false);
  const [selectedRole, setSelectedRole] = useState(null);

  const openRoleDialog = (role = null) => {
    setSelectedRole(role);
    setIsRoleDialogOpen(true);
  };

  const handleRoleSave = (role) => {
    if (selectedRole) {
      updateRole(role);
    } else {
      addRole(role);
    }
    setIsRoleDialogOpen(false);
  };

  const openDeleteDialog = (role) => {
    setSelectedRole(role);
    setIsDeleteDialogOpen(true);
  };

  const handleDeleteConfirm = () => {
    deleteRole(selectedRole.id);
    setIsDeleteDialogOpen(false);
  };

  const columns: GridColDef[] = [
    { field: 'name', headerName: 'Role Name', width: 200 },
    {
      field: 'permissions',
      headerName: 'Permissions',
      width: 300,
      renderCell: (params) => (
        <>
          {params.value.map((permissionId) => (
            <Chip key={permissionId} label={permissionId} style={{ margin: 2 }} />
          ))}
        </>
      ),
    },
    {
      field: 'actions',
      headerName: 'Actions',
      sortable: false,
      width: 150,
      renderCell: (params) => (
        <>
          <Button color="primary" onClick={() => openRoleDialog(params.row)}>
            Edit
          </Button>
          <Button color="secondary" onClick={() => openDeleteDialog(params.row)}>
            Delete
          </Button>
        </>
      ),
    },
  ];

  return (
    <div>
      <Button color="primary" onClick={() => openRoleDialog()}>
        Add Role
      </Button>
      <CommonGrid rows={roles} columns={columns} />
      <RoleDialog 
        open={isRoleDialogOpen} 
        role={selectedRole} 
        onSave={handleRoleSave} 
        onClose={() => setIsRoleDialogOpen(false)} 
      />
      <DeleteConfirmationDialog
        open={isDeleteDialogOpen}
        onClose={() => setIsDeleteDialogOpen(false)}
        onConfirm={handleDeleteConfirm}
      />
    </div>
  );
};

export default RolesTab;

// ... other imports
import { Group } from './types';

interface GroupDialogProps {
  open: boolean;
  group?: Group;
  onSave: (group: Group) => void;
  onClose: () => void;
}

const GroupDialog: React.FC<GroupDialogProps> = ({ open, group, onSave, onClose }) => {
  const [name, setName] = useState('');
  const [subGroups, setSubGroups] = useState<string[]>([]);
  const [subGroupName, setSubGroupName] = useState('');

  useEffect(() => {
    if (group) {
      setName(group.name);
      setSubGroups(group.subGroups || []);
    } else {
      setName('');
      setSubGroups([]);
    }
  }, [group]);

  const handleSave = () => {
    const savedGroup: Group = {
      id: group ? group.id : Math.random().toString(36).substr(2, 9),
      name: name,
      parentId: group?.parentId || null,
      subGroups: subGroups,
    };
    onSave(savedGroup);
    onClose();
  };

  const handleAddSubGroup = () => {
    if (subGroupName && !subGroups.includes(subGroupName)) {
      setSubGroups([...subGroups, subGroupName]);
      setSubGroupName('');
    }
  };

  const handleDeleteSubGroup = (subGroupNameToDelete: string) => {
    setSubGroups(subGroups.filter(name => name !== subGroupNameToDelete));
  };

  return (
    <Dialog open={open} onClose={onClose}>
      <DialogTitle>{group ? 'Edit Group' : 'Add Group'}</DialogTitle>
      <DialogContent>
        <TextField
          autoFocus
          margin="dense"
          id="name"
          label="Group Name"
          type="text"
          fullWidth
          value={name}
          onChange={(e) => setName(e.target.value)}
        />
        <TextField
          margin="dense"
          id="sub-group-name"
          label="Subgroup Name"
          type="text"
          fullWidth
          value={subGroupName}
          onChange={(e) => setSubGroupName(e.target.value)}
          onKeyPress={(e) => { if (e.key === 'Enter') { e.preventDefault(); handleAddSubGroup(); } }}
        />
        <div style={{ marginTop: '10px' }}>
          {subGroups.map((subGroup, index) => (
            <Chip
              key={index}
              label={subGroup}
              onDelete={() => handleDeleteSubGroup(subGroup)}
              style={{ margin: '5px' }}
            />
          ))}
        </div>
      </DialogContent>
      <DialogActions>
        <Button onClick={onClose} color="primary">Cancel</Button>
        <Button onClick={handleSave} color="primary">Save</Button>
      </DialogActions>
    </Dialog>
  );
};

export default GroupDialog;

------29/1-------

  import React, { useState, useEffect } from 'react';
import { Dialog, DialogTitle, DialogContent, TextField, DialogActions, Button, Select, MenuItem, Chip } from '@material-ui/core';
import { Group, SubGroup, UseCase } from './types';

interface GroupDialogProps {
  open: boolean;
  group?: Group;
  onSave: (group: Group) => void;
  onClose: () => void;
  useCases: UseCase[]; // Array of use cases for selection
}

const GroupDialog: React.FC<GroupDialogProps> = ({ open, group, onSave, onClose, useCases }) => {
  const [name, setName] = useState('');
  const [subGroups, setSubGroups] = useState<SubGroup[]>([]);

  useEffect(() => {
    if (group) {
      setName(group.name);
      setSubGroups(group.subGroups || []);
    } else {
      setName('');
      setSubGroups([]);
    }
  }, [group]);

  const handleSubGroupNameChange = (index, value) => {
    const updatedSubGroups = subGroups.map((subGroup, idx) =>
      index === idx ? { ...subGroup, subGroupName: value } : subGroup
    );
    setSubGroups(updatedSubGroups);
  };

  const handleUseCaseChange = (index, useCaseId) => {
    const updatedSubGroups = subGroups.map((subGroup, idx) =>
      index === idx ? { ...subGroup, useCaseId } : subGroup
    );
    setSubGroups(updatedSubGroups);
  };

  const handleSave = () => {
    const savedGroup: Group = {
      id: group ? group.id : Math.random().toString(36).substr(2, 9),
      name,
      subGroups,
    };
    onSave(savedGroup);
    onClose();
  };

  const handleAddSubGroup = () => {
    setSubGroups([...subGroups, { subGroupId: Math.random().toString(36).substr(2, 9), subGroupName: '', useCaseId: '' }]);
  };

  const handleDeleteSubGroup = (subGroupIdToDelete: string) => {
    setSubGroups(subGroups.filter(subGroup => subGroup.subGroupId !== subGroupIdToDelete));
  };

  return (
    <Dialog open={open} onClose={onClose}>
      <DialogTitle>{group ? 'Edit Group' : 'Add Group'}</DialogTitle>
      <DialogContent>
        <TextField
          autoFocus
          margin="dense"
          id="name"
          label="Group Name"
          type="text"
          fullWidth
          value={name}
          onChange={(e) => setName(e.target.value)}
        />
        {subGroups.map((subGroup, index) => (
          <div key={subGroup.subGroupId}>
            <TextField
              margin="dense"
              label="Subgroup Name"
              type="text"
              fullWidth
              value={subGroup.subGroupName}
              onChange={(e) => handleSubGroupNameChange(index, e.target.value)}
            />
            <Select
              value={subGroup.useCaseId}
              onChange={(e) => handleUseCaseChange(index, e.target.value)}
              fullWidth
            >
              {useCases.map(useCase => (
                <MenuItem key={useCase.id} value={useCase.id}>{useCase.name}</MenuItem>
              ))}
            </Select>
            <Button onClick={() => handleDeleteSubGroup(subGroup.subGroupId)}>Delete Subgroup</Button>
          </div>
        ))}
        <Button onClick={handleAddSubGroup}>Add Subgroup</Button>
      </DialogContent>
      <DialogActions>
        <Button onClick={onClose} color="primary">Cancel</Button>
        <Button onClick={handleSave} color="primary">Save</Button>
      </DialogActions>
    </Dialog>
  );
};

export default GroupDialog;


import React, { useState, useEffect } from 'react';
import { Dialog, DialogTitle, DialogContent, TextField, DialogActions, Button, Select, MenuItem } from '@material-ui/core';
import { Group, SubGroup, UseCase } from './types';

const GroupDialog = ({ open, group, onSave, onClose, useCases }) => {
  // ... existing state declarations

  useEffect(() => {
    // ... existing useEffect logic
  }, [group]);

  // ... existing handler functions

  const handleUseCaseChange = (index, useCaseId) => {
    // ... existing logic for handling use case change
  };

  const handleRemoveUseCase = (index) => {
    const updatedSubGroups = subGroups.map((subGroup, idx) =>
      index === idx ? { ...subGroup, useCaseId: '' } : subGroup // Remove use case by setting it to an empty string
    );
    setSubGroups(updatedSubGroups);
  };

  const handleSave = () => {
    // ... existing save logic
  };

  // ... other existing functions

  return (
    <Dialog open={open} onClose={onClose}>
      <DialogTitle>{group ? 'Edit Group' : 'Add Group'}</DialogTitle>
      <DialogContent>
        <TextField
          autoFocus
          margin="dense"
          id="name"
          label="Group Name"
          type="text"
          fullWidth
          value={name}
          onChange={(e) => setName(e.target.value)}
        />
        {subGroups.map((subGroup, index) => (
          <div key={subGroup.subGroupId}>
            <TextField
              margin="dense"
              label="Subgroup Name"
              type="text"
              fullWidth
              value={subGroup.subGroupName}
              onChange={(e) => handleSubGroupNameChange(index, e.target.value)}
            />
            <Select
              value={subGroup.useCaseId}
              onChange={(e) => handleUseCaseChange(index, e.target.value)}
              fullWidth
            >
              <MenuItem value=""><em>None</em></MenuItem>
              {useCases.map(useCase => (
                <MenuItem key={useCase.id} value={useCase.id}>{useCase.name}</MenuItem>
              ))}
            </Select>
            <Button onClick={() => handleRemoveUseCase(index)}>Remove Use Case</Button>
            <Button onClick={() => handleDeleteSubGroup(subGroup.subGroupId)}>Delete Subgroup</Button>
          </div>
        ))}
        <Button onClick={handleAddSubGroup}>Add Subgroup</Button>
      </DialogContent>
      <DialogActions>
        <Button onClick={onClose} color="primary">Cancel</Button>
        <Button onClick={handleSave} color="primary">Save</Button>
      </DialogActions>
    </Dialog>
  );
};

export default GroupDialog;
