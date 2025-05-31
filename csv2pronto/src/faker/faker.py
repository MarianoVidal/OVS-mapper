ML_PREFIX = "ML"


class Faker:
    "Class that anonimyzes data."

    sites: dict[str, str] = {
        "argenprop": "site1",
        "mercadolibre": "site2",
        "zonaprop": "site3",
        "desconocido": "site4"
    }

    @classmethod
    def anonymize(cls, row: dict) -> dict:
        """Anonimyzes the data in a row."""
        row = row.copy()

        if row.get("listing_id", None):
            row["listing_id"] = cls.id(row["listing_id"])

        # Mariano: Colocar un sitio temporal mientras
        #          averiguo una mejor opción
        sitio_temp = "site4"

        #          Hacer un try por si falta este atributo
        try:
            row["site"] = cls.site(row["site"])
        except KeyError as ke:
            row["site"] = sitio_temp

        row["url"] = None

        return row

    @classmethod
    def site(cls, site: str) -> str:
        "Anonimyzes a site."
        return cls.sites[site.lower()]

    @classmethod
    def id(cls, id: str) -> str | None:
        "Anoniymyzes an id."
        return id[2:] if id.startswith(ML_PREFIX) else id
