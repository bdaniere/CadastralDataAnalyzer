from pathlib import Path
import requests


class GeoServerClient:

    def __init__(
        self,
        url: str = "http://localhost:8080/geoserver",
        username: str = "admin",
        password: str = "admin",
    ):
        self.url = url.rstrip("/")
        self.auth = (username, password)

    def _check_response(self, response):
        if not response.ok:
            raise RuntimeError(
                f"GeoServer error {response.status_code}\n"
                f"{response.text}"
            )


    def element_exists(
        self,
        workspace_name: str,
        element_type: str,
        element_name: str | None = None,
    ) -> bool:
        """
        Checking whether an element (workspace / datastore / styles / layer) exists on a Geoserver
        """

        paths = {
            "workspace": "",
            "datastore": f"/datastores/{element_name}",
            "style": f"/styles/{element_name}.sld",
            "layer": f"/layers/{element_name}",
        }

        try:
            suffix = paths[element_type]
        except KeyError:
            raise NotImplementedError(
                f"element_exists error: "
                f"{element_type} not implemented yet"
            )

        response = requests.get(
            (
            f"{self.url}/rest/workspaces/"
            f"{workspace_name}{suffix}"
        ),
            auth=self.auth
        )

        return response.status_code == 200


    def create_workspace(self, workspace_name: str):
        if self.element_exists(workspace_name, "workspace"):
            return

        response = requests.post(
            f"{self.url}/rest/workspaces",
            auth=self.auth,
            headers={"Content-Type": "text/xml"},
            data=f"""
                    <workspace>
                        <name>{workspace_name}</name>
                    </workspace>
                """,
        )

        if response.status_code not in (201, 401, 403):
            self._check_response(response)

        return response


    def create_postgis_store(
        self,
        workspace: str,
        store_name: str,
        db_name: str,
        host: str,
        port: int,
        user: str,
        password: str,
        schema: str = "raw_data",
    ):

        if self.element_exists(workspace, "datastore", store_name):
            return

        xml = f"""
        <dataStore>
            <name>{store_name}</name>
            <connectionParameters>
                <entry key="dbtype">postgis</entry>
                <entry key="host">{host}</entry>
                <entry key="port">{port}</entry>
                <entry key="database">{db_name}</entry>
                <entry key="schema">{schema}</entry>
                <entry key="user">{user}</entry>
                <entry key="passwd">{password}</entry>
            </connectionParameters>
        </dataStore>
        """

        response = requests.post(
            f"{self.url}/rest/workspaces/{workspace}/datastores",
            auth=self.auth,
            headers={"Content-Type": "text/xml"},
            data=xml,
        )

        self._check_response(response)

        return response


    def create_style(
        self,
        workspace: str,
        style_name: str,
        sld_file: str,
    ):

        if self.element_exists(workspace, "style", style_name) :
            return 
        
        response = requests.post(
            f"{self.url}/rest/workspaces/{workspace}/styles"
            f"?name={style_name}",
            auth=self.auth,
            headers={
                "Content-Type":
                "application/vnd.ogc.sld+xml"
            },
            data=Path(sld_file).read_text(
            encoding="utf-8"
        ),
        )
        self._check_response(response)

        return response

    def publish_table(
        self,
        workspace: str,
        store_name: str,
        table_name: str,
        style_name: str | None = None,
    ):
        xml = f"""
        <featureType>
            <name>{table_name}</name>
        </featureType>
        """

        if self.element_exists(workspace, "layer", table_name):
            return

        response = requests.post(
            f"{self.url}/rest/workspaces/{workspace}"
            f"/datastores/{store_name}/featuretypes",
            auth=self.auth,
            headers={"Content-Type": "text/xml"},
            data=xml,
        )

        self._check_response(response)

        if style_name:
            layer_xml = f"""
            <layer>
                <defaultStyle>
                    <name>{style_name}</name>
                </defaultStyle>
            </layer>
            """

            layer_response = requests.put(
                f"{self.url}/rest/layers/"
                f"{workspace}:{table_name}",
                auth=self.auth,
                headers={"Content-Type": "text/xml"},
                data=layer_xml,
            )

            response = self._check_response(layer_response)

        return response

    def delete_workspace(
        self,
        workspace_name: str,
        recurse: bool = True,
    ):
        response = requests.delete(
            f"{self.url}/rest/workspaces/{workspace_name}",
            auth=self.auth,
            params={
                "recurse": str(recurse).lower()
            }
        )

        if response.status_code == 404:
            print(
                f"Workspace '{workspace_name}' "
                "does not exist"
            )
            return

        self._check_response(response)

# ██████╗ ███████╗██████╗ ██╗   ██╗ ██████╗ 
# ██╔══██╗██╔════╝██╔══██╗██║   ██║██╔════╝ 
# ██║  ██║█████╗  ██████╔╝██║   ██║██║  ███╗
# ██║  ██║██╔══╝  ██╔══██╗██║   ██║██║   ██║
# ██████╔╝███████╗██████╔╝╚██████╔╝╚██████╔╝
# ╚═════╝ ╚══════╝╚═════╝  ╚═════╝  ╚═════╝                                         

from glob import glob
from pathlib import Path

tables_styles={
    "batiments" : "batiments",
    "communes" : "Communes_simples",
    "parcelles" : "Zones_simple"
    }

if __name__ == "__main__":
    toto = GeoServerClient()
    toto.create_workspace('raw_data_workspace')
    toto.create_postgis_store(workspace="raw_data_workspace", store_name="raw_data_store", db_name="cadastral_data", host="postgis", port=5432, user="postgres", password="postgres", schema="raw_data")
    for style_path in glob("styles/*.sld"):
        toto.create_style(workspace="raw_data_workspace", style_name=Path(style_path).stem, sld_file=style_path)
    for table_name, style_name in tables_styles.items():
        toto.publish_table(workspace="raw_data_workspace", store_name="raw_data_store", table_name=table_name, style_name=style_name)

    # breakpoint()
    # toto.delete_workspace(workspace_name="raw_data_workspace", recurse = True)