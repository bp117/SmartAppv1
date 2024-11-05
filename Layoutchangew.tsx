import React, { useState, useRef } from "react";
import {
  Button,
  Dialog,
  Input,
  Select,
  Text,
  Sheet,
  Accordion,
  Toaster,
  Joyride,
  AlertDialog
} from "your-ui-library"; // Replace with your actual UI library imports

const PlaygroundPage = () => {
  const [selectedFolder, setSelectedFolder] = useState(null);
  const [isNewFolder, setIsNewFolder] = useState(false);
  const [selectedModel, setSelectedModel] = useState("");
  const [userMessage, setUserMessage] = useState("");
  const [alertBoxIsOpen, setAlertBoxIsOpen] = useState(false);
  const [messages, setMessages] = useState([]);
  const messagesEndRef = useRef(null);

  const clearMessages = () => setMessages([]);
  const handleFileChange = (e) => {
    // Handle file input change logic here
  };
  const handleInputChange = (e) => {
    setUserMessage(e.target.value);
  };
  const handleSend = () => {
    // Handle sending message logic here
  };
  const handleDecline = () => setAlertBoxIsOpen(false);
  const handleAccept = () => {
    // Handle acceptance logic here
  };

  return (
    <div className="flex w-full h-screen">
      {/* Left Section - Document Sources */}
      <div className="w-[300px] h-full p-4 bg-gray-100 overflow-y-auto">
        <Text variant="large">Document Sources</Text>
        {/* Add document source management components here */}
      </div>

      {/* Middle Section - Chat Interface */}
      <div className="flex flex-col w-1/2 border-x bg-white h-full">
        
        {/* Top Section - Clear and System Instructions */}
        <div className="flex justify-between p-4 bg-gray-200 flex-shrink-0">
          <Button onClick={clearMessages}>Clear</Button>
          <Accordion type="single" collapsible>
            <Accordion.Item value="system-instructions">
              <Accordion.Trigger>System Instructions</Accordion.Trigger>
              <Accordion.Content className="overflow-y-auto max-h-40">
                {/* System Instructions content goes here */}
                <Text>Here are the system instructions...</Text>
              </Accordion.Content>
            </Accordion.Item>
          </Accordion>
        </div>

        {/* Message Content Section - Scrollable */}
        <div className="flex-1 overflow-y-auto p-4">
          {messages.length === 0 ? (
            <Text variant="muted">Send a message to start your chat</Text>
          ) : (
            messages.map((message, index) => (
              <div key={index} className="mb-2">
                <Text>{message.content}</Text>
              </div>
            ))
          )}
          <div ref={messagesEndRef} />
        </div>

        {/* Bottom Section - Input and Send Button */}
        <div className="p-4 bg-gray-200 flex items-center flex-shrink-0">
          <Input
            placeholder="Enter the message"
            value={userMessage}
            onChange={handleInputChange}
            className="flex-grow mr-2"
          />
          <Button
            disabled={!userMessage.trim()}
            onClick={handleSend}
            variant="secondary"
            size="small"
          >
            Send
          </Button>
        </div>
      </div>

      {/* Right Section - Settings */}
      <div className="w-[300px] h-full p-4 bg-gray-100 overflow-y-auto">
        <Sheet>
          <div className="flex justify-start p-2">
            <Button size="small" variant="default">Settings Icon</Button>
          </div>
          <div className="p-4">
            <Text variant="large">Model Parameters</Text>
            {/* Add model parameters and settings components here */}
          </div>
        </Sheet>
      </div>

      {/* Alert Dialog for User Agreement */}
      <AlertDialog open={alertBoxIsOpen} onOpenChange={setAlertBoxIsOpen}>
        <AlertDialogContent>
          <AlertDialogTitle>Playground User Agreement</AlertDialogTitle>
          <AlertDialogDescription>
            Do not upload any confidential, sensitive, or inappropriate content to this platform.
          </AlertDialogDescription>
          <div className="flex justify-end gap-2">
            <Button onClick={handleDecline}>Decline</Button>
            <Button onClick={handleAccept} variant="primary">Accept</Button>
          </div>
        </AlertDialogContent>
      </AlertDialog>

      {/* Toaster and Joyride for onboarding or tours */}
      <Toaster />
      <Joyride
        steps={[
          { target: ".selector1", content: "Step 1" },
          { target: ".selector2", content: "Step 2" }
        ]}
        continuous
        showSkipButton
      />
    </div>
  );
};

export default PlaygroundPage;
