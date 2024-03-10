from classifier.classifier import *

# Assuming you have set your train and validation directories
train_dir = 'path/to/train/data'
validation_dir = 'path/to/validation/data'

model = build_cnn_model()

train_generator, validation_generator = prepare_data(train_dir, validation_dir)

train_model(model, train_generator, validation_generator, epochs=10)

save_model(model, "my_model.h5")

# load the model and use it for prediction
loaded_model = load_model_from_file("my_model.h5")

predicted_class = predict_image(loaded_model, "path/to/your/image.jpg")

print("Predicted class:", predicted_class)