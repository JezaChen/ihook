import sys
import pathlib

file_path = pathlib.Path(__file__).resolve()
dir_path = file_path.parent

# Add the local and third_party directories to the path
sys.path.extend([str(dir_path / 'local'), str(dir_path / 'third_party')])

# Now, we can import the local and third_party packages as namespace packages
import package.a  # noqa
import package.b  # noqa

package.a.func()
package.b.func()
