#!/usr/bin/osascript

-- Setup script to help user create a global hotkey for Fast YouTrack

display dialog "Fast YouTrack Hotkey Setup

To set up a global hotkey (like Cmd+Shift+T):

1. Open System Preferences > Keyboard > Shortcuts
2. Click 'App Shortcuts' in the sidebar  
3. Click the '+' button
4. Set Application to 'All Applications'
5. Set Menu Title to: Fast YouTrack GUI
6. Set Keyboard Shortcut to: Cmd+Shift+T (or your preference)
7. Click 'Add'

Then create an Automator Quick Action:
1. Open Automator > New > Quick Action
2. Add 'Run Shell Script' action
3. Set shell to: /bin/bash
4. Paste this command:
   cd " & quoted form of (do shell script "dirname " & quoted form of (POSIX path of (path to me)) & " | xargs dirname | xargs dirname") & " && python3 run.py --gui

5. Save as 'Fast YouTrack GUI'
6. Go to System Preferences > Keyboard > Shortcuts > Services
7. Find 'Fast YouTrack GUI' and assign your hotkey

Would you like me to create the Automator action for you?" buttons {"Manual Setup", "Create Action"} default button "Create Action"

set userChoice to button returned of result

if userChoice is "Create Action" then
    -- Get project root
    set scriptPath to POSIX path of (path to me)
    set projectRoot to do shell script "dirname " & quoted form of scriptPath & " | xargs dirname | xargs dirname"
    
    -- Create the automator workflow
    set workflowContent to "<?xml version=\"1.0\" encoding=\"UTF-8\"?>
<!DOCTYPE plist PUBLIC \"-//Apple//DTD PLIST 1.0//EN\" \"http://www.apple.com/DTDs/PropertyList-1.0.dtd\">
<plist version=\"1.0\">
<dict>
	<key>AMApplicationBuild</key>
	<string>523</string>
	<key>AMApplicationVersion</key>
	<string>2.10</string>
	<key>AMDocumentVersion</key>
	<string>2</string>
	<key>actions</key>
	<array>
		<dict>
			<key>action</key>
			<dict>
				<key>AMAccepts</key>
				<dict>
					<key>Container</key>
					<string>List</string>
					<key>Optional</key>
					<true/>
					<key>Types</key>
					<array>
						<string>com.apple.cocoa.string</string>
					</array>
				</dict>
				<key>AMActionVersion</key>
				<string>2.0.3</string>
				<key>AMApplication</key>
				<array>
					<string>Automator</string>
				</array>
				<key>AMParameterProperties</key>
				<dict>
					<key>COMMAND_STRING</key>
					<dict>
						<key>tokenizedValue</key>
						<array>
							<string>cd " & quoted form of projectRoot & " && python3 run.py --gui</string>
						</array>
					</dict>
					<key>CheckedForUserDefaultShell</key>
					<true/>
					<key>inputMethod</key>
					<integer>0</integer>
					<key>shell</key>
					<string>/bin/bash</string>
					<key>source</key>
					<string></string>
				</dict>
				<key>AMProvides</key>
				<dict>
					<key>Container</key>
					<string>List</string>
					<key>Types</key>
					<array>
						<string>com.apple.cocoa.string</string>
					</array>
				</dict>
				<key>ActionBundlePath</key>
				<string>/System/Library/Automator/Run Shell Script.action</string>
				<key>ActionName</key>
				<string>Run Shell Script</string>
				<key>ActionParameters</key>
				<dict>
					<key>COMMAND_STRING</key>
					<string>cd " & quoted form of projectRoot & " && python3 run.py --gui</string>
					<key>CheckedForUserDefaultShell</key>
					<true/>
					<key>inputMethod</key>
					<integer>0</integer>
					<key>shell</key>
					<string>/bin/bash</string>
					<key>source</key>
					<string></string>
				</dict>
				<key>BundleIdentifier</key>
				<string>com.apple.RunShellScript</string>
				<key>CFBundleVersion</key>
				<string>2.0.3</string>
				<key>CanShowSelectedItemsWhenRun</key>
				<false/>
				<key>CanShowWhenRun</key>
				<true/>
				<key>Category</key>
				<array>
					<string>AMCategoryUtilities</string>
				</array>
				<key>Class Name</key>
				<string>RunShellScriptAction</string>
				<key>InputUUID</key>
				<string>A0B3FE8E-8EAE-4C93-BCE4-9C91B2E7A1A5</string>
				<key>Keywords</key>
				<array>
					<string>Shell</string>
					<string>Script</string>
					<string>Command</string>
					<string>Run</string>
					<string>Unix</string>
				</array>
				<key>OutputUUID</key>
				<string>3F4E6D6A-5C44-4F48-A5E5-E6A4A4A2A2A2</string>
				<key>UUID</key>
				<string>A0B3FE8E-8EAE-4C93-BCE4-9C91B2E7A1A5</string>
				<key>UnlocalizedApplications</key>
				<array>
					<string>Automator</string>
				</array>
				<key>arguments</key>
				<dict>
					<key>0</key>
					<dict>
						<key>default value</key>
						<string>cd " & quoted form of projectRoot & " && python3 run.py --gui</string>
						<key>name</key>
						<string>COMMAND_STRING</string>
						<key>required</key>
						<string>0</string>
						<key>type</key>
						<string>0</string>
						<key>uuid</key>
						<string>0</string>
					</dict>
				</dict>
				<key>conversionLabel</key>
				<integer>0</integer>
				<key>isViewVisible</key>
				<true/>
				<key>location</key>
				<string>449.000000:316.000000</string>
				<key>nibPath</key>
				<string>/System/Library/Automator/Run Shell Script.action/Contents/Resources/Base.lproj/main.nib</string>
			</dict>
		</dict>
	</array>
	<key>connectors</key>
	<array/>
	<key>workflowMetaData</key>
	<dict>
		<key>workflowTypeIdentifier</key>
		<string>com.apple.Automator.servicesMenu</string>
	</dict>
</dict>
</plist>"
    
    set workflowPath to (path to desktop as text) & "Fast YouTrack GUI.workflow"
    
    try
        do shell script "mkdir -p " & quoted form of (POSIX path of workflowPath) & "/Contents"
        do shell script "echo " & quoted form of workflowContent & " > " & quoted form of (POSIX path of workflowPath) & "/Contents/document.wflow"
        
        display dialog "Automator workflow created on Desktop!

Now:
1. Double-click 'Fast YouTrack GUI.workflow' on Desktop to install
2. Go to System Preferences > Keyboard > Shortcuts > Services  
3. Find 'Fast YouTrack GUI' and assign Cmd+Shift+T

The workflow has been saved to your Desktop." buttons {"OK"} default button "OK"
        
    on error errorMsg
        display dialog "Error creating workflow: " & errorMsg buttons {"OK"} default button "OK" with icon caution
    end try
end if