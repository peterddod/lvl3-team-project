import subprocess
from pathlib import Path
import os

BASE_DIR = Path(__file__).resolve().parent.parent.parent
MEDIA_DIR = os.path.join(BASE_DIR,'media')
USER_DIR = os.path.join(MEDIA_DIR, 'users')
TEST_DIR = os.path.join(MEDIA_DIR, 'tests')
#DOCKER IMAGE BEING USED
dimage = "coding-image" 

def run_container(filename, input_file):
    #RUNS AND COMPILES FILE IN CONTAINER

    #create a container from the specified image
    proc = subprocess.Popen(["docker","create", dimage], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    encoded_containerID, error = proc.communicate()
    if proc.returncode != 0:
        return ['Error creating container', error]
    else:
        containerID = encoded_containerID.decode("utf-8")[:12]
        print("ContID: ", containerID)
        #copy the files to run (and compile if necessary) to the container
        subprocess.run([ "docker", "cp", filename, containerID + ":" + "/testing"])
        subprocess.run(["docker", "cp", input_file, containerID + ":" + "/input"])
        #run the container
        runCont = subprocess.Popen(["sudo", "docker", "container", "start", "-a", containerID], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        #get outputs or errors
        output, error = runCont.communicate()

        
        if len(error) != 0:
            return['error', error]
        else:
            return['worked', output]


def add_language_extension(filename, language):
    language_mapping = {'java':'.java', 'python':'.py', 'c':'.c'}

    if language in language_mapping:
        return filename + language_mapping[language]
    else:
        raise Exception('language not supported')


def test(testname, username, language, input=None): 
    #note----Name here is hardcoded
    filename = os.path.join(USER_DIR, username, testname, add_language_extension('main', language))
    #testing adding language extension
    print("IN TEST ", filename)
    testfolder = os.path.join(TEST_DIR, testname)
    
    test_cases = os.listdir(os.path.join(testfolder, 'input'))

    outputs = []
    
    if input==None:
        testingInput = 'noncustom'
    else:
        testingInput = input


    #Results for run
    passes = 0
    fails = 0
    result = 0
    if testingInput == 'noncustom':
        for i, test_case in enumerate(test_cases):
            out_str = "Test Case " + str(i+1) + ":\n"
            testingInput = os.path.join(testfolder, 'input', test_case.strip())
            output = run_container(filename, testingInput)
            if output[0] == 'error':
                out_str+=output[1].decode('ascii')
            else:
                with open(os.path.join(testfolder, 'output', test_case.strip()), 'r') as f:
                    data = f.read()
                    #test case result
                    result = data.strip() == output[1].strip().decode("ASCII")
                    out_str += str(result) +"\n"
                    out_str += output[1].strip().decode("ASCII") + "\n"
            outputs.append(out_str + "\n")
        
            if result != 0:
                passes += 1
            else:
                fails +=1
        return outputs, passes, fails
    else:
        output = run_container(filename, testingInput)
        #add error handling
        return ["Custom testing", output[1]]

def test2(testname, username, language, input=None):
    filename = os.path.join(USER_DIR, username, testname, 'temp',  add_language_extension('main', language))
  
    testfolder = os.path.join(TEST_DIR, testname)
    
    
    test_cases = os.listdir(os.path.join(testfolder, 'input'))

    outputs = []

    for i, test_case in enumerate(test_cases):
        out_str = "Test Case " + str(i+1) + ":\n"
        output = run_container(filename, os.path.join(testfolder, 'input', test_case.strip()))
        if output[0] == 'error':
            out_str+=output[1].decode('ascii')
            print(out_str)
        else:
            with open(os.path.join(testfolder, 'output', test_case.strip()), 'r') as f:
                data = f.read()
                out_str += str(data.strip() == output[1].strip().decode("ASCII")) +"\n"
                out_str += output[1].strip().decode("ASCII") + "\n"
        
        outputs.append(out_str + "\n") 
    return outputs




