import React, { useState, useEffect } from 'react';
import { Stepper, Step, StepLabel, Button, Box, Typography, Container, Card } from '@mui/material';
import FileUpload from './components/FileUpload';
import SchemaFileUpload from './components/SchemaFileUpload';
import MappingTable from './components/MappingTable';
import RecordIdentifierSelection from './components/RecordIdentifierSelection';
import SqlCheckTable from './components/SqlCheckTable';
import SqlToXmlConverter from './components/SqlToXmlConverter';
import axios from 'axios';

const steps = [
    'Upload Config YAML and SQL Files',
    'Upload Schema/Data Files',
    'Map Fields and Approve Mappings',
    'Select Record Identifier and Generate SQL Checks',
    'Generate Job'
];

function App() {
    const [activeStep, setActiveStep] = useState(0);
    const [sourceAliases, setSourceAliases] = useState([]);
    const [schemas, setSchemas] = useState({});
    const [mappedSchemas, setMappedSchemas] = useState({});
    const [approvedMappings, setApprovedMappings] = useState({});
    const [generatedSqlChecks, setGeneratedSqlChecks] = useState({});
    const [mappedFieldOptions, setMappedFieldOptions] = useState([]); // New state for dynamic options

    const handleNext = () => setActiveStep((prevActiveStep) => prevActiveStep + 1);
    const handleBack = () => setActiveStep((prevActiveStep) => prevActiveStep - 1);
    const [recordIdFields, setRecordIdFields] = useState({});
    // Fetch mapped field options from the backend
    useEffect(() => {
        axios.get(`${process.env.REACT_APP_API_URL}/get_mapped_field_options`)
            .then(response => {
                setMappedFieldOptions(response.data.mapped_field_options || []);
                console.log("Mapped Field Options:", response.data.mapped_field_options);  // Log options
            })
            .catch(error => console.error("Error fetching mapped field options:", error));
    }, []);


    const handleUploadComplete = (aliases) => {
        setSourceAliases(aliases);
        handleNext();
    };

    const handleSchemasUploaded = (data) => {
        const inferredSchemas = {};
        const mappedSchemasData = {};
        Object.keys(data.inferred_schemas).forEach(alias => {
            inferredSchemas[alias] = data.inferred_schemas[alias] || [];
            mappedSchemasData[alias] = data.mapped_schemas[alias] || [];
        });
        setSchemas(inferredSchemas);
        setMappedSchemas(mappedSchemasData);
        handleNext();
    };

    const handleApproveMappings = (alias, mappings) => {
        setApprovedMappings(prev => ({ ...prev, [alias]: mappings }));
    };

    const handleGenerateSqlChecks = (alias, recordId, schema) => {
        const data = {
            alias,
            record_id_field: recordId,
            mappings: schema
        };

        axios.post(`${process.env.REACT_APP_API_URL}/generate_sql_checks`, data)
            .then(response => {
                if (response.status === 200) {
                    setGeneratedSqlChecks(prev => ({ ...prev, [alias]: response.data.sql_checks }));
                    setRecordIdFields(prev => ({ ...prev, [alias]: recordId }));
                }
            })
            .catch(error => {
                console.error("Error generating SQL checks:", error);
            });
    };

    const handleSaveSqlChecks = (alias, sqlChecks) => {
        setGeneratedSqlChecks(prev => ({ ...prev, [alias]: sqlChecks }));
    };

    useEffect(() => {
        console.log("Updated SQL Checks:", generatedSqlChecks);
    }, [generatedSqlChecks]);

    const renderStepContent = (stepIndex) => {
        switch (stepIndex) {
            case 0:
                return <FileUpload onUploadComplete={handleUploadComplete} />;
            case 1:
                return <SchemaFileUpload sourceAliases={sourceAliases} onSchemasUploaded={handleSchemasUploaded} />;
            case 2:
                return sourceAliases.map(alias => (
                    <MappingTable
                        key={`${alias}-mapping`}
                        alias={alias}
                        schema={mappedSchemas[alias] || []}
                        mappedFieldOptions={mappedFieldOptions} // Pass options for dropdown
                        onApproveMappings={handleApproveMappings}
                    />
                ));
            case 3:
                return (
                    <Box>
                        {sourceAliases.map(alias => (
                            <RecordIdentifierSelection
                                key={`${alias}-selection`}
                                alias={alias}
                                schema={approvedMappings[alias] || []}
                                onGenerateSqlChecks={handleGenerateSqlChecks}
                            />
                        ))}
                        {Object.keys(generatedSqlChecks).length > 0 && (
                            <Box mt={4}>
                                {sourceAliases.map(alias => (
                                    <SqlCheckTable
                                        key={`${alias}-table`}
                                        alias={alias}
                                        sqlChecks={generatedSqlChecks[alias] || []} // Pass SQL checks for each alias
                                        onSaveChecks={handleSaveSqlChecks}
                                    />
                                ))}
                            </Box>
                        )}
                    </Box>
                );
            case 4:
                return <SqlToXmlConverter recordIdFields={recordIdFields} />;
            default:
                return <Typography>Unknown step</Typography>;
        }
    };

    return (
        <Container maxWidth="lg">
            <Box mt={4}>
                <Typography variant="h4" gutterBottom align="center">ETL Workflow</Typography>
            </Box>
            <Stepper activeStep={activeStep} alternativeLabel>
                {steps.map((label) => (
                    <Step key={label}>
                        <StepLabel>{label}</StepLabel>
                    </Step>
                ))}
            </Stepper>
            <Box mt={4}>
                <Card variant="outlined" sx={{ p: 3 }}>
                    {renderStepContent(activeStep)}
                </Card>
            </Box>
            <Box display="flex" justifyContent="space-between" mt={4}>
                <Button disabled={activeStep === 0} onClick={handleBack}>Back</Button>
                {activeStep < steps.length - 1 ? (
                    <Button
                        variant="contained"
                        color="primary"
                        onClick={handleNext}
                        disabled={activeStep === 3 && Object.keys(generatedSqlChecks).length < sourceAliases.length}
                    >
                        Next
                    </Button>
                ) : (
                    <Button variant="contained" color="primary" onClick={() => setActiveStep(0)}>Reset</Button>
                )}
            </Box>
        </Container>
    );
}

export default App;
