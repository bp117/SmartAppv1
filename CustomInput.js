import React from 'react';
import TextField from '@mui/material/TextField';

const CustomInput = ({ label, type, value, onChange }) => {
    return (
        <TextField
            label={label}
            type={type}
            value={value}
            onChange={onChange}
            variant="outlined"
            fullWidth
        />
    );
};

export default CustomInput;
