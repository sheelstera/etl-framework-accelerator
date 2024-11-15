// SchemaFileUpload.js
import React, { useState } from 'react';
import { Button, Box, Typography } from '@mui/material';
import { styled } from '@mui/system';
import axios from 'axios';

// Styled hidden input
const StyledInput = styled('input')({
    display: 'none'
});

function SchemaFileUpload({ sourceAliases, onSchemasUploaded }) {
    const [files, setFiles] = useState({});

    const handleFileChange = (alias, event) => {
        setFiles({ ...files, [alias]: event.target.files[0] });
    };

    const handleSchemaUpload = async () => {
        const formData = new FormData();
        sourceAliases.forEach(alias => {
            if (files[alias]) {
                formData.append(alias, files[alias]);
            }
        });

        try {
            const response = await axios.post(`${process.env.REACT_APP_API_URL}/upload_schema_files`, formData);
            onSchemasUploaded(response.data);
        } catch (error) {
            console.error("Error uploading schema files:", error);
        }
    };

    return (
        <Box textAlign="center">
            <Typography variant="h6">Step 2: Upload Schema/Data Files for Each Source</Typography>
            {sourceAliases.map(alias => (
                <Box key={alias} mt={2}>
                    <Typography>{`Upload file for source alias: ${alias}`}</Typography>
                    <label htmlFor={`file-upload-${alias}`}>
                        <StyledInput
                            id={`file-upload-${alias}`}
                            type="file"
                            onChange={(e) => handleFileChange(alias, e)}
                        />
                        <Button variant="contained" component="span">
                            {files[alias] ? files[alias].name : `Choose File for ${alias}`}
                        </Button>
                    </label>
                </Box>
            ))}
            <Button
                variant="contained"
                color="primary"
                onClick={handleSchemaUpload}
                disabled={Object.keys(files).length !== sourceAliases.length}
                sx={{ mt: 2 }}
            >
                Upload Files
            </Button>
        </Box>
    );
}

export default SchemaFileUpload;
