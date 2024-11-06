import React, { useState } from "react";
import {
  Button,
  Input,
  Text,
  Dialog,
  DataTable,
  Toaster,
  Tooltip,
  Checkbox
} from "your-ui-library"; // Replace with your actual UI library imports

const FileUploadPage = () => {
  const [showUploadDialog, setShowUploadDialog] = useState(false);
  const [uploadFiles, setUploadFiles] = useState([]);
  const [selectedFiles, setSelectedFiles] = useState([]);
  const [isDelete, setIsDelete] = useState(false);

  const handleFileUpload = (files) => {
    // Handle file upload logic here
    setUploadFiles(files);
  };

  const handleDelete = () => {
    // Handle delete logic here
    setIsDelete(false);
  };

  return (
    <div className="w-full flex pb-3 gap-4 bg-card h-full overflow-hidden">
  <div className="flex flex-col w-full h-full">

    {/* Upload Section */}
    <div className="flex flex-row w-full gap-2 mb-4">
      <div className="w-full flex flex-col gap-2">
        <div className="flex justify-center items-center gap-2 ml-6 mt-4 mb-4">
          <CloudUpload strokeWidth={0.5} size={32} />
          <input
            type="file"
            accept=".pdf,.txt,.doc,.docx,.csv,.json"
            ref={inputRef}
            multiple
            className="hidden"
            onChange={(e) =>
              handleFileUpload(Array.from(e.target.files as FileList))
            }
          />
          <Text variant="large">Drag and Drop your files here or click to upload</Text>
          <Text variant="default">Supported formats include .pdf, .txt, .json (only for custom chunking strategy)</Text>
        </div>
      </div>
    </div>

    {/* Data Table Section */}
    <div className="flex flex-col gap-2 bg-card text-card-foreground shadow-sm rounded-lg border p-4 h-full overflow-hidden">
      <Text variant="medium" className="pb-2">Uploaded Files</Text>
      <div className="overflow-y-auto max-h-[50vh] px-2">
        <DataTable
          columns={uploadColumns}
          data={docManagementList}
          filterColumn="documentName"
          rowSelection={rowSelection}
          setRowSelection={setRowSelection}
          className="lg:max-h-[50px] xl:max-h-[150px] overflow-y-auto"
        />
      </div>
    </div>

    {/* Action Buttons */}
    <div className="flex justify-end items-center gap-4 mt-4">
      <Button variant="secondary" size="small" onClick={() => navigate("/myapps")}>
        Cancel
      </Button>
      <Button variant="default" size="small" onClick={checkValidDocs}>
        Continue
      </Button>
    </div>
  </div>

  {/* Delete Confirmation Dialog */}
  <Dialog open={isDelete} onOpenChange={() => setIsDelete(false)}>
    <DialogContent className="sm:max-w-[475px]">
      <DialogHeader>
        <DialogTitle>Delete Document</DialogTitle>
      </DialogHeader>
      <DialogDescription>
        Are you sure you want to delete the document <strong>permanently</strong>?
      </DialogDescription>
      <DialogFooter>
        <Button onClick={() => setIsDelete(false)} variant="secondary">No</Button>
        <Button onClick={deleteDoc} variant="destructive">Yes</Button>
      </DialogFooter>
    </DialogContent>
  </Dialog>

  {/* Warning Dialog */}
  <Dialog open={showWarningDialog} onOpenChange={() => setShowWarningDialog(false)}>
    <DialogContent className="sm:max-w-[475px]">
      <DialogHeader>
        <DialogTitle>Warning</DialogTitle>
      </DialogHeader>
      <DialogDescription>
        No docs/invalid docs will result in erroneous search results. Do you want to continue?
      </DialogDescription>
      <DialogFooter>
        <Button onClick={() => setShowWarningDialog(false)} variant="secondary">Cancel</Button>
        <Button onClick={handleContinue} variant="default">Continue</Button>
      </DialogFooter>
    </DialogContent>
  </Dialog>

  {/* Upload Dialog */}
  <Dialog open={openUpload} onOpenChange={() => setOpenUpload(false)}>
    <DialogContent className="slim-scrollbar">
      <DialogTitle>Upload Documents</DialogTitle>
      <Separator orientation="horizontal" size="2" />
      <DataList.Root>
        {uploadFiles.map((file, index) => (
          <DataList.Item key={file.fileName}>
            <DataList.Label minWidth="80px">
              <Checkbox
                checked={file.checked}
                onCheckedChange={(value) => handleCheckBox(file.fileName, value)}
                className="h-5 w-5"
              />
            </DataList.Label>
            <DataList.Value>
              {file.fileName.endsWith(".pdf") ? (
                <FileText color="red" />
              ) : (
                <FileText color="blue" />
              )}
              <Text variant="medium">{file.fileName}</Text>
              {file.duplicate && (
                <Tooltip>
                  <TooltipTrigger asChild>
                    <TriangleAlert className="h-6 w-6" color="orange" />
                  </TooltipTrigger>
                  <TooltipContent>
                    <p>This file already exists. Uploading again will override existing data</p>
                  </TooltipContent>
                </Tooltip>
              )}
            </DataList.Value>
          </DataList.Item>
        ))}
      </DataList.Root>
      <DialogFooter>
        <Button onClick={() => setOpenUpload(false)} variant="secondary">Cancel</Button>
        <Button onClick={doFileUpload} disabled={uploadFiles.length === 0}>Proceed</Button>
      </DialogFooter>
    </DialogContent>
  </Dialog>
</div>
  );
};

export default FileUploadPage;
