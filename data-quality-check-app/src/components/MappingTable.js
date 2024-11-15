import React, { useState, useEffect } from 'react';
import { Table, TableBody, TableCell, TableContainer, TableHead, TableRow, Paper, TextField, Button, Typography, Box, Select, MenuItem, IconButton } from '@mui/material';
import { Add, Delete } from '@mui/icons-material';

function MappingTable({ schema, onApproveMappings, alias, mappedFieldOptions }) {
    const [updatedSchema, setUpdatedSchema] = useState([]);

    useEffect(() => {
        setUpdatedSchema(schema);
    }, [schema]);

    const handleUserFieldChange = (index, value) => {
        const newSchema = [...updatedSchema];
        newSchema[index].user_field = value;
        setUpdatedSchema(newSchema);
    };

    const handleMappingChange = (index, value) => {
        const newSchema = [...updatedSchema];
        newSchema[index].mapped_field = value;
        setUpdatedSchema(newSchema);
    };

    const handleAddMapping = () => {
        setUpdatedSchema(prevSchema => [...prevSchema, { user_field: '', mapped_field: '' }]);
    };

    const handleRemoveMapping = (index) => {
        const newSchema = updatedSchema.filter((_, i) => i !== index);
        setUpdatedSchema(newSchema);
    };

    const handleApprove = async () => {
        await onApproveMappings(alias, updatedSchema);
    };

    return (
        <Box>
            <Typography variant="h6">{`Mapping Fields for Source: ${alias}`}</Typography>
            <TableContainer component={Paper}>
                <Table>
                    <TableHead>
                        <TableRow>
                            <TableCell>User Field</TableCell>
                            <TableCell>Mapped Field</TableCell>
                            <TableCell>Actions</TableCell>
                        </TableRow>
                    </TableHead>
                    <TableBody>
                        {updatedSchema.map((field, index) => (
                            <TableRow key={index}>
                                <TableCell>
                                    <TextField
                                        fullWidth
                                        value={field.user_field || ""}
                                        onChange={(e) => handleUserFieldChange(index, e.target.value)}
                                    />
                                </TableCell>
                                <TableCell>
                                    <Select
                                        fullWidth
                                        value={field.mapped_field || ""}
                                        onChange={(e) => handleMappingChange(index, e.target.value)}
                                        displayEmpty
                                    >
                                        <MenuItem value="" disabled>Select Mapped Field</MenuItem>
                                        {mappedFieldOptions.map((option, idx) => (
                                            <MenuItem key={idx} value={option}>
                                                {option}
                                            </MenuItem>
                                        ))}
                                    </Select>
                                </TableCell>
                                <TableCell>
                                    <IconButton onClick={() => handleRemoveMapping(index)} color="secondary">
                                        <Delete />
                                    </IconButton>
                                </TableCell>
                            </TableRow>
                        ))}
                    </TableBody>
                </Table>
            </TableContainer>
            <Button
                variant="contained"
                color="primary"
                onClick={handleAddMapping}
                startIcon={<Add />}
                sx={{ mt: 2 }}
            >
                Add Mapping
            </Button>
            <Button variant="contained" color="primary" onClick={handleApprove} sx={{ mt: 2, ml: 2 }}>
                Approve Mappings
            </Button>
        </Box>
    );
}

export default MappingTable;
