import wave
import tkinter as tk
from tkinter import Canvas, filedialog
import struct

def openAndReadWav(path):
    # initializing these as none in case there is a premature return (e.g., invalid file format)
    leftChannel = rightChannel = frameRate = numFrames = None

    # validate file format
    with open(path, 'rb') as file:
        chunkDescriptor = file.read(12)
        if chunkDescriptor[0:4] != b'RIFF' or chunkDescriptor[8:12] != b'WAVE':
            print("The file is not a valid WAV file.")
            return
    
    # open wave file and collect parameters using wave module
    with wave.open(path, 'rb') as waveFile:
        numChannels = waveFile.getnchannels()
        sampleWidth = waveFile.getsampwidth()
        frameRate = waveFile.getframerate()
        numFrames = waveFile.getnframes()
        audioFrames = waveFile.readframes(numFrames)

        # normalize audio frames with bit shift to get range of values between -1 and 1
        def normalize(frame, width):
            # calculate maximum sample value based on width and divide it by 2 to find max posiitve int value 
            maxSampleValue = float(int((1 << (width * 8)) / 2))
            # assume samples are either 16 or 8 bits, as per the assignment
            return frame / maxSampleValue if width == 2 else (frame - 128) / maxSampleValue

        # ensure sample is either 8 or 16 bits (i.e., 1 or 2 bytes)
        if sampleWidth == 1 or sampleWidth == 2:
            formatString = f"<{numFrames * numChannels}{'B' if sampleWidth == 1 else 'h'}"
            audioData = struct.unpack(formatString, audioFrames)
        
            # initialize channels as empty lists
            leftChannel = []
            rightChannel = []

            # loop through unpacked audio data for left channel
            for i in range(0, len(audioData), 2):  # step by 2 because every other frame is for the left channel
                frame = audioData[i]
                normalized_sample = normalize(frame, sampleWidth)
                leftChannel.append(normalized_sample)

            # loop through unpacked audio data for right channel
            for i in range(1, len(audioData), 2):
                frame = audioData[i]
                normalized_sample = normalize(frame, sampleWidth)
                rightChannel.append(normalized_sample)

        else:
            print("Unsupported sample width")
            return

    return leftChannel, rightChannel, frameRate, numFrames

    
def plotWaveform(leftChannel, rightChannel, frameRate, numFrames):
    # new window
    plotWindow = tk.Toplevel()
    plotWindow.title("Waveform Plot")

    # canvas size
    canvasWidth = 800
    canvasHeight = 400

    canvas = Canvas(plotWindow, width=canvasWidth, height=canvasHeight, bg='white')
    canvas.pack()

    # scaling to fit wave on canvas
    xScale = canvasWidth / numFrames

    # separating the scale calculations for left and right channels 
    # so that the two don't overlap when the waveforms are plotted
    yScaleLeft = (canvasHeight / 8) / max(max(leftChannel), abs(min(leftChannel)))
    yScaleRight = (canvasHeight / 8) / max(max(rightChannel), abs(min(rightChannel)))

    textPad = 20
    verticalPadding = 50

    canvasHeightAdjusted = canvasHeight - 2 * verticalPadding

    # plot left channel waveform
    prevYLeft = verticalPadding + canvasHeightAdjusted / 4
    for i, frame in enumerate(leftChannel):
        x = i * xScale
        yLeft = verticalPadding + (canvasHeightAdjusted / 4) - (frame * yScaleLeft)
        canvas.create_line(i * xScale, prevYLeft, x, yLeft, fill='blue')
        prevYLeft = yLeft

    # plot right channel waveform
    prevYRight = verticalPadding + 3 * canvasHeightAdjusted / 4
    for i, frame in enumerate(rightChannel):
        x = i * xScale
        yRight = verticalPadding + (3 * canvasHeightAdjusted / 4) - (frame * yScaleRight)
        canvas.create_line(i * xScale, prevYRight, x, yRight, fill='red')
        prevYRight = yRight

    # labels
    canvas.create_text(textPad, verticalPadding / 2, anchor='w', text="Left Channel", fill='blue')
    # moving right channel to avoid overlap with y axis label
    canvas.create_text(textPad, verticalPadding + canvasHeightAdjusted / 2 + verticalPadding / 2, anchor='w', text="Right Channel", fill='red')
    canvas.create_text(canvasWidth / 2, canvasHeight - textPad, text="Time (samples)", fill='black')
    canvas.create_text(textPad / 2, canvasHeight / 2, text="Amplitude", fill='black', angle=90)
    canvas.create_text(canvasWidth - textPad, textPad, anchor='ne', text=f"Sample Rate: {frameRate} Hz")
    canvas.create_text(canvasWidth - textPad, textPad * 2, anchor='ne', text=f"Number of Samples: {numFrames}")

    plotWindow.mainloop()


# GUI code
window = tk.Tk()
window.withdraw()

wavFilePath = filedialog.askopenfilename(title="Select a .wav file", filetypes=[("WAV files", "*.wav")])

if wavFilePath:
    leftChannel, rightChannel, frameRate, numFrames = openAndReadWav(wavFilePath)

    if leftChannel and rightChannel and frameRate and numFrames:
        plotWaveform(leftChannel, rightChannel, frameRate, numFrames)

