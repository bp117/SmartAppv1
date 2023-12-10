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


import React, { useState, useEffect } from 'react';
import { Dialog, DialogTitle, DialogContent, TextField, DialogActions, Button, Chip } from '@material-ui/core';
import { Group } from './types';

interface GroupDialogProps {
  open: boolean;
  group?: Group;
  onSave: (group: Group) => void;
  onClose: () => void;
}

const GroupDialog: React.FC<GroupDialogProps> = ({ open, group, onSave, onClose }) => {
  const [name, setName] = useState('');
  const [subGroupNames, setSubGroupNames] = useState<string[]>([]); // Store subgroup names
  const [subGroupNameInput, setSubGroupNameInput] = useState(''); // Input for new subgroup name

  useEffect(() => {
    if (group) {
      setName(group.name);
      setSubGroupNames(group.subGroups.map(subGroup => subGroup.name));
    } else {
      setName('');
      setSubGroupNames([]);
    }
  }, [group]);

  const handleSave = () => {
    const savedGroup: Group = {
      ...group,
      name,
      id: group ? group.id : Math.random().toString(36).substr(2, 9),
      subGroups: subGroupNames.map(name => ({ id: Math.random().toString(36).substr(2, 9), name })),
    };
    onSave(savedGroup);
    onClose();
  };

  const handleAddSubGroup = () => {
    if (subGroupNameInput) {
      setSubGroupNames([...subGroupNames, subGroupNameInput]);
      setSubGroupNameInput('');
    }
  };

  const handleDeleteSubGroup = (nameToDelete: string) => {
    setSubGroupNames(subGroupNames.filter(name => name !== nameToDelete));
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
          value={subGroupNameInput}
          onChange={(e) => setSubGroupNameInput(e.target.value)}
          onKeyPress={(e) => { if (e.key === 'Enter') { e.preventDefault(); handleAddSubGroup(); } }}
        />
        <div style={{ marginTop: '10px' }}>
          {subGroupNames.map((subGroupName, index) => (
            <Chip
              key={index}
              label={subGroupName}
              onDelete={() => handleDeleteSubGroup(subGroupName)}
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
