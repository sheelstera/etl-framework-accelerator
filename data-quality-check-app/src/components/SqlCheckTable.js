import React, { useState, useEffect } from 'react';
import { Table, TableBody, TableCell, TableContainer, TableHead, TableRow, Paper, TextField, Button, Typography, Box, IconButton } from '@mui/material';
import { Add, Delete } from '@mui/icons-material';

function SqlCheckTable({ alias, sqlChecks, onSaveChecks }) {
    const [editedSqlChecks, setEditedSqlChecks] = useState(sqlChecks);

    useEffect(() => {
        setEditedSqlChecks(sqlChecks);
    }, [sqlChecks]);

    const handleSqlChange = (index, value) => {
        const newSqlChecks = [...editedSqlChecks];
        newSqlChecks[index] = value;
        setEditedSqlChecks(newSqlChecks);
    };

    const handleAddSqlCheck = () => {
        setEditedSqlChecks(prevChecks => [...prevChecks, { user_field: '', check_type: '', sql: '' }]);
    };

    const handleRemoveSqlCheck = (index) => {
        const newSqlChecks = editedSqlChecks.filter((_, i) => i !== index);
        setEditedSqlChecks(newSqlChecks);
    };

    const handleSave = () => {
        onSaveChecks(alias, editedSqlChecks);
    };

    return (
        <Box mt={4}>
            <Typography variant="h6">{`SQL Checks for Source: ${alias}`}</Typography>
            <TableContainer component={Paper} sx={{ mt: 2 }}>
                <Table>
                    <TableHead>
                        <TableRow>
                            <TableCell>Field</TableCell>
                            <TableCell>Check Type</TableCell>
                            <TableCell>SQL Statement</TableCell>
                            <TableCell>Actions</TableCell>
                        </TableRow>
                    </TableHead>
                    <TableBody>
                        {editedSqlChecks.map((check, index) => (
                            <TableRow key={index}>
                                <TableCell>
                                    <TextField
                                        fullWidth
                                        variant="outlined"
                                        value={check.user_field}
                                        onChange={(e) => handleSqlChange(index, { ...check, user_field: e.target.value })}
                                    />
                                </TableCell>
                                <TableCell>
                                    <TextField
                                        fullWidth
                                        variant="outlined"
                                        value={check.check_type}
                                        onChange={(e) => handleSqlChange(index, { ...check, check_type: e.target.value })}
                                    />
                                </TableCell>
                                <TableCell>
                                    <TextField
                                        fullWidth
                                        variant="outlined"
                                        value={check.sql}
                                        onChange={(e) => handleSqlChange(index, { ...check, sql: e.target.value })}
                                        sx={{ width: '650px' }}  // Adjusted width for SQL statements
                                    />
                                </TableCell>
                                <TableCell>
                                    <IconButton onClick={() => handleRemoveSqlCheck(index)} color="secondary">
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
                onClick={handleAddSqlCheck}
                startIcon={<Add />}
                sx={{ mt: 2 }}
            >
                Add SQL Check
            </Button>
            <Button variant="contained" color="primary" onClick={handleSave} sx={{ mt: 2, ml: 2 }}>
                Save SQL Checks
            </Button>
        </Box>
    );
}

export default SqlCheckTable;
