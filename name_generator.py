import random 
import subprocess
import re 
import os
class C:
    DB_PATH = "names.md" 

class NameGenerator:
    def __init__(self, db_path: str=None):
        """
        Initialize the NameGenerator with a database path.
        :param db_path: Path to the database file. If None, defaults to C.DB_PATH.
        """
        self.db_path = db_path or C.DB_PATH 
        self.match_fn = self.match_with_regex if self.get_file_size() > 50*1024 else self.match_with_grep 
        self._available_category = self.list_category() 

    def list_category(self):
        """
        List all available categories in the database.
        :return: List of categories.
        """
        with open(self.db_path, "r") as file:
            lines = file.readlines()
            return [line[1:].split(":")[0].strip() for line in lines if line.startswith("#")] 

    def load_db(self):
        """
        Load the database file into memory.
        :return: Content of the database file.
        """
        if self.db_path:
            with open(self.db_path, "r") as file:
                return file.read()
        else:
            raise ValueError("Database path is not specified.")

    def get_file_size(self):
        """
        Get the size of the database file in KB.
        :return: Size of the file in KB.
        """
        return os.path.getsize(self.db_path) / 1024
        

    def match_with_regex(self, st: str, sc: str):
        """
        Match a section in the database using regex.
        :param st: Section title to match.
        :param sc: Subcategory to match.
        :return: Matched line.
        """
        hasattr(self, 'text') or self.load_db() 
        pattern = (
            r"#.*" + re.escape(st) + r".*\n"      
            r"((?:^(?!#).*\n?)*)"                 
        )

        match = re.search(pattern, self.text, flags=re.MULTILINE)

        if match:
            section = match.group(1)
            for line in section.splitlines():
                if line.strip().startswith(f"{sc}:"):
                    return line.strip() 
        return ""
    
    def match_with_grep(self, st: str, sc: str):
        """
        Match a section in the database using grep.
        :param st: Section title to match.
        :param sc: Subcategory to match.
        :return: Matched line.
        """
        grep1 = subprocess.Popen(
            ["grep", "-A", "26", "-P", f"^#.*{st}.*", self.db_path],
            stdout=subprocess.PIPE
        )
        grep2 = subprocess.Popen(
            ["grep", f"^{sc}:"],
            stdin=grep1.stdout,
            stdout=subprocess.PIPE,
            text=True
        )

        # Ensure no resource leaks
        grep1.stdout.close()
        output, _ = grep2.communicate()

        return output.strip()  
        

    def generate(self, starts_with: str=None, category: str=None):
        """
        Generate a name based on the provided starting letters and category.
        :param starts_with: Starting letters for the name.
        :param category: Category to match.
        :return: Generated name.
        """
        starts_with = starts_with or random.choice('ABCDEFGHIJKLMNOPQRSTUVWXYZ') 
        category = category or random.choice(self._available_category)
        
        result = []
        
        ocatgory = category
        if len(category.split(",")) == 1 and len(starts_with.split(",")) > 1:
            category = ','.join([category] * len(starts_with.split(","))) 
        
        print(f"starts_with: {starts_with}; category: {category}") 

        for sc, st in zip(starts_with.split(","), category.split(",")):
            match = self.match_fn(st, sc)
            if not match:
                return f"Category '{st}' not found in the database.: {st}"  
            match = random.choice(match.split(":", 1)[1].strip().split(",")) 
            result.append(match.strip())
        
        # print(result)
        result = '-'.join([self.remove_special_chars(name) for name in result]) + ': ' + ocatgory.replace(",", "-")
        return result 

    def remove_special_chars(self, name: str):
        """
        Remove special characters from a name.
        :param name: Name to clean.
        :return: Cleaned name.
        """
        return re.sub(r"[^a-zA-Z0-9]", "", name)


    def __call__(self, starts_with: str=None, category: str=None):
        """
        Call the generate method when the object is called.
        :param starts_with: Starting letters for the name.
        :param category: Category to match.
        :return: Generated name.
        """
        return self.generate(starts_with, category)  

get_new_name = NameGenerator() 





if __name__ == "__main__":
    print(get_new_name())