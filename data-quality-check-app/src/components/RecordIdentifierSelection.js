// RecordIdentifierSelection.js
import React, { useState } from 'react';
import { Button, Box, Typography, Select, MenuItem } from '@mui/material';

function RecordIdentifierSelection({ alias, schema, onGenerateSqlChecks }) {
    const [recordId, setRecordId] = useState('');

    const handleGenerateClick = () => {
        if (recordId && onGenerateSqlChecks) {
            onGenerateSqlChecks(alias, recordId, schema);  // Pass alias, recordId, and schema
        }
    };

    return (
        <Box textAlign="center" mt={4}>
            <Typography variant="h6">{`Step 4: Select Record Identifier for ${alias}`}</Typography>
            <Typography>Select the record identifier field from the list below:</Typography>
            <Select
                value={recordId}
                onChange={(e) => setRecordId(e.target.value)}
                displayEmpty
                fullWidth
                variant="outlined"
                sx={{ mt: 2 }}
            >
                <MenuItem value="" disabled>
                    Choose Record Identifier
                </MenuItem>
                {schema.map((field, index) => (
                    <MenuItem key={index} value={field.user_field}>
                        {field.user_field}
                    </MenuItem>
                ))}
            </Select>
            <Button
                variant="contained"
                color="primary"
                onClick={handleGenerateClick}
                disabled={!recordId}
                sx={{ mt: 2 }}
            >
                Generate SQL Checks
            </Button>
        </Box>
    );
}

export default RecordIdentifierSelection;
