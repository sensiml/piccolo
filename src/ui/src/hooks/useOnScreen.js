/*
Copyright 2017-2024 SensiML Corporation

This file is part of SensiML™ Piccolo AI™.

SensiML Piccolo AI is free software: you can redistribute it and/or
modify it under the terms of the GNU Affero General Public License
as published by the Free Software Foundation, either version 3 of
the License, or (at your option) any later version.

SensiML Piccolo AI is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU
Affero General Public License for more details.

You should have received a copy of the GNU Affero General Public
License along with SensiML Piccolo AI. If not, see <https://www.gnu.org/licenses/>.
*/

import { useState, useEffect } from "react";

const useOnScreen = (ref, rootMargin) => {
  const [isIntersecting, setIntersecting] = useState(false);

  const observer = new IntersectionObserver(([entry]) => setIntersecting(entry.isIntersecting), {
    rootMargin: rootMargin || "0px",
    threshold: 1.0,
  });

  // eslint-disable-next-line consistent-return
  useEffect(() => {
    if (ref) {
      observer.observe(ref.current);
      // Remove the observer as soon as the component is unmounted
      return () => observer.disconnect();
    }
  }, []);

  return isIntersecting;
};

export default useOnScreen;
