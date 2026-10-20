from tensorflow.keras import layers
import tensorflow as tf
import pathlib as pt

base_dir = pt.Path("/workspaces/Yusuf-Zaheer/")

class ModelMaker:
    def __init__(self):
        pass

    def load_model(self, name):
        self.model = tf.keras.models.load_model(base_dir / f'{name}.keras')

    def load_local_dataset(self, img_size=(224, 224)):
        self.train_ds, self.test_ds = tf.keras.utils.image_dataset_from_directory(
        base_dir / "Dataset",
        labels="inferred",
        label_mode="int",
        image_size=img_size,
        batch_size=32,
        validation_split=0.15,
        subset="both",
        seed=1,
        )
        
        self.train_ds = self.train_ds.cache().shuffle(1000).prefetch(buffer_size=tf.data.AUTOTUNE)
        self.test_ds = self.test_ds.cache().prefetch(buffer_size=tf.data.AUTOTUNE)
        
    def create_model(self, output, img_size=(224, 224, 3), optimizer="adam", loss="sparse_categorical_crossentropy", metrics=["accuracy"]):
        
        self.model = tf.keras.Sequential([

            layers.Input(shape=img_size),
            #layers.Rescaling(1/255.0),
            
            #1st convolutional layer
            layers.Conv2D(filters=16, kernel_size=5, strides=1, activation="relu"),
            layers.MaxPool2D(pool_size=2, padding="same"),
            layers.BatchNormalization(),
        
            #2nd convolutional layer
            layers.Conv2D(filters=32, kernel_size=3, strides=1, activation="relu"),
            layers.MaxPool2D(pool_size=2, padding="same"),
            layers.BatchNormalization(),
            
            #3rd convolutional layer
            layers.Conv2D(filters=48, kernel_size=3, strides=1, activation="relu"),        
            layers.MaxPool2D(pool_size=2, padding="same"),
            layers.BatchNormalization(),
            
            #4th convolutional layer
            layers.Conv2D(filters=64, kernel_size=3, strides=1, activation="relu"),
            layers.BatchNormalization(),
            
            layers.Flatten(),
            
            #dense layers
            layers.Dense(units=128, activation="relu"),
            layers.Dense(units=192, activation="relu"),
            
            layers.Dense(units=output, activation="softmax")
        ])
    
        self.model.summary()
        self.model.compile(
            optimizer=optimizer,
            loss=loss,
            metrics=metrics
        )
        
    def train_model(self, min_delta=0.0005,batch_size=32, epochs=32, patience=8):
        early_stopping = tf.keras.callbacks.EarlyStopping(
            monitor="val_loss",
            min_delta=min_delta,
            patience=patience,
            restore_best_weights=True,
            verbose=1
        )
        
        logger = tf.keras.callbacks.CSVLogger(
            base_dir / "logs.csv", 
            separator=",",
            append=False
        )
    
        self.history = self.model.fit(
            self.train_ds,
            validation_data=self.val_ds,
            epochs=epochs,
            batch_size=batch_size,
            callbacks=[early_stopping, logger],
            verbose=1
        )
        
        #model evaluation through data visualisation
         
        #save model
        print("\n", "#"*50)
        if "y" == input("Save model? [y/n]"):
            name = input("Please enter model name: ")
            self.model.save(base_dir / "tools/models" / f"{name}.keras")
            
        print("\n", "#"*50)
