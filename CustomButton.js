import React from 'react';
import Button from '@mui/material/Button';

const CustomButton = ({ children, variant, color, onClick }) => {
    return (
        // modify the button to not occupy the full width of the container
        
        <Button variant={variant} color={color} onClick={onClick}>
            {children}
        </Button>
    );
};

export default CustomButton;
