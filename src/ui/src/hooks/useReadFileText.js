import { useEffect, useState } from "react";

const useReadFileText = (fileURL) => {
  const [text, setText] = useState("");

  useEffect(() => {
    fetch(fileURL)
      .then((response) => response.text())
      .then((_text) => {
        setText(_text);
      });
  }, []);

  return text;
};

export default useReadFileText;
