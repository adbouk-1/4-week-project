#Import the modules
import tensorflow as tf
from tensorflow.keras.preprocessing.image import ImageDataGenerator
from tensorflow.keras.models import load_model


def build_cnn_model():
    """
    Builds a convolutional neural network (CNN) model.

    Returns:
    -tf.keras.Sequential: The CNN model.

    The CNN model consists of the following layers:
    - Conv2D layer with 24 filters, kernel size of (3,3), and ReLU activation function.
    - MaxPool2D layer with pool size of (2,2).
    - Conv2D layer with 36 filters, kernel size of (3,3), and ReLU activation function.
    - MaxPool2D layer with pool size of (2,2).
    - Flatten layer.
    - Dense layer with 128 units and ReLU activation function.
    - Dense layer with 2 units and softmax activation function. This will result in a binary output with 1 digit representing the fault and the other representing no fault

    The model is compiled with the following settings:
    - Optimizer: Adam with learning rate of 1e-3.
    - Loss function: sparse_categorical_crossentropy.
    - Metrics: accuracy.
    """

    cnn_model = tf.keras.Sequential([

        tf.keras.layers.Conv2D(filters=24, kernel_size=(3,3), activation=tf.nn.relu, input_shape=(1000, 1000, 3)),

        tf.keras.layers.MaxPool2D(pool_size=(2,2)),

        tf.keras.layers.Conv2D(filters=36, kernel_size=(3,3), activation=tf.nn.relu),

        tf.keras.layers.MaxPool2D(pool_size=(2,2)),

        tf.keras.layers.Flatten(),
        tf.keras.layers.Dense(128, activation=tf.nn.relu),

        tf.keras.layers.Dense(2, activation=tf.nn.softmax)
    ])

    cnn_model.compile(optimizer=tf.keras.optimizers.Adam(learning_rate=1e-3),
                loss='sparse_categorical_crossentropy',
                metrics=['accuracy'])

    return cnn_model

def prepare_data(train_dir, validation_dir):
    """
    Prepares the data for training and validation.

    Parameters:
    - train_dir (str): The directory path containing the training images.
    - validation_dir (str): The directory path containing the validation images.

    Note:
    - Inside each directory, the folder structure should be as follows:
        -Fault
            -Image1.jpg
            -Image2.jpg
            -...
        -NoFault
            -Image1.jpg
            -Image2.jpg
            -...   

    Returns:
    - train_generator (ImageDataGenerator): The generator for training data.
    - validation_generator (ImageDataGenerator): The generator for validation data.
    """

    train_datagen = ImageDataGenerator(rescale=1./255)
    train_generator = train_datagen.flow_from_directory(
            train_dir,
            target_size=(1000, 1000),
            batch_size=2,
            class_mode='binary')  # Use 'categorical' for multi-class classification

    validation_datagen = ImageDataGenerator(rescale=1./255)
    validation_generator = validation_datagen.flow_from_directory(
            validation_dir,
            target_size=(1000, 1000),
            batch_size=2,
            class_mode='binary')  # Use 'categorical' for multi-class classification
    
    return train_generator, validation_generator

def train_model(model, train_generator, validation_generator, epochs=3):
    """
    Train the given model using the provided data generators.

    Parameters:
    - model (object): The model to be trained.
    - train_generator (object): The data generator for the training set.
    - validation_generator (object): The data generator for the validation set.
    - epochs (int): The number of epochs to train the model (default=3).

    Returns:
    - history (object): The training history object.

    """

    history = model.fit(
        train_generator,
        steps_per_epoch=10,  # Adjust based on the number of images in the training set
        epochs=epochs,
        validation_data=validation_generator,
        validation_steps=10)  # Adjust based on the number of images in the validation set
    return history


def evaluate_model(model, test_images, test_labels):
    """
    Evaluate the performance of a given model on a test dataset.

    Parameters:
    - model: The trained model to be evaluated.
    - test_images: The input images of the test dataset.
    - test_labels: The corresponding labels of the test dataset.

    Returns:
    - test_loss: The loss value of the model on the test dataset.
    - test_acc: The accuracy of the model on the test dataset.

    """

    test_loss, test_acc = model.evaluate(test_images, test_labels)
    return test_loss, test_acc


def load_model_from_file(model_name="./models/model.h5"):
    """
    Load a Keras model from a file.

    Parameters:
    - model_name (str): The path to the model file. Default is "./models/model.h5".

    Returns:
    - model (Keras model): The loaded Keras model.

    """

    model = load_model(model_name)
    print("Model loaded from", model_name)
    return model

def save_model(model, model_name="./models/model.h5"):
    """
    Save the trained model to a specified file.

    Parameters:
        model (keras.Model): The trained model to be saved.
        model_name (str): The name or path of the file to save the model. Default is "./models/model.h5".

    Returns:
        None

    """

    model.save(model_name)
    print("Model saved as", model_name)

def predict_image(model, image_path):
    """
    Predicts the class probabilities for an input image using a given model.

    Parameters:
        model (tf.keras.Model): The trained model to use for prediction.
        image_path (str): The path to the input image file.

    Returns:
        numpy.ndarray: An array of class probabilities for the input image.

    """

    img = tf.keras.preprocessing.image.load_img(image_path, target_size=(1000, 1000))
    img_array = tf.keras.preprocessing.image.img_to_array(img)
    img_array = tf.expand_dims(img_array, 0)  # Create a batch

    predictions = model.predict(img_array)
    return predictions

