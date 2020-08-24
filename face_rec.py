import face_recognition as fr
from os import path


class Face:
    def __init__(self, app):
        self.storage = app.config["storage"]
        self.db = app.db
        self.faces = [] # store face in an array format
        self.known_faces_encodings = []
        self.face_user_keys = {}
        self.load_all()

    def load_user_by_index_key(self, index_key=0):
        key_str = str(index_key)

        if key_str in self.face_user_keys:
            return self.face_user_keys[key_str]
        return None

    def load_train_file_by_name(self, name):
        trained_storage = path.join(self.storage, 'trained')
        return path.join(trained_storage, name)

    def load_unknown_file_by_name(self,name):
        unknown_storage = path.join(self.storage,'unknown')
        return path.join(unknown_storage, name)

    def load_all(self):
        # print("hey")
        results = self.db.select('SELECT faces.id, faces.user_id, faces.filename, faces.created FROM faces')

        for row in results:
            print(row)
            user_id = row[1]
            filename = row[2]
            face = {
                "id": row[0],
                "user_id": user_id,
                "filename": filename,
                "created": row[3]
            }
            self.faces.append(face)

            face_image = fr.load_image_file(self.load_train_file_by_name(filename))
            face_image_encodings = fr.face_encodings(face_image)[0]
            index_key = len(self.known_faces_encodings)
            self.known_faces_encodings.append(face_image_encodings)
            self.face_user_keys['{0}'.format(str(index_key))] = user_id
        # print(self.known_faces_encodings)

    def recognize(self, unknown_file):
        unknown_image = fr.load_image_file(self.load_unknown_file_by_name(unknown_file))
        unknown_image_encodings = fr.face_encodings(unknown_image)[0]

        results = fr.compare_faces(self.known_faces_encodings, unknown_image_encodings, tolerance=0.6)

        print("results:",results)
        index_key = 0
        for matched in results:
            if matched:
                # find user by id
                user_id = self.load_user_by_index_key(index_key)
                return user_id
            index_key = index_key + 1

        return None
