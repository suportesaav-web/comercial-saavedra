"""
Cliente de Conexão e Extração da API Ploomes CRM - Comercial Saavedra.
Responsável por autenticar, paginar com OData e normalizar tarefas do CRM em DataFrames.
"""

from typing import Callable, Dict, Any, List, Optional, Tuple
import os
import time
import requests
import pandas as pd
from datetime import datetime
from pathlib import Path


def get_default_api_key_and_url() -> Tuple[str, str]:
    """Obtém credenciais padrão de settings, secrets ou variáveis de ambiente."""
    try:
        from app.config.settings import get_ploomes_credentials
        return get_ploomes_credentials()
    except Exception:
        key = os.environ.get("PLOOMES_API_KEY", "")
        url = os.environ.get("PLOOMES_BASE_URL", "https://api2.ploomes.com")
        return key, url


class PloomesClient:
    """Cliente HTTP para comunicação com a API v2 do Ploomes CRM."""

    def __init__(
        self,
        api_key: Optional[str] = None,
        base_url: Optional[str] = None,
        timeout: int = 35,
        max_retries: int = 4
    ):
        default_key, default_url = get_default_api_key_and_url()
        self.api_key = api_key or default_key
        self.base_url = (base_url or default_url).rstrip("/")
        self.timeout = timeout
        self.max_retries = max_retries

    @property
    def headers(self) -> Dict[str, str]:
        return {
            "User-Key": self.api_key,
            "Content-Type": "application/json",
            "Accept": "application/json"
        }

    def test_connection(self) -> Tuple[bool, str]:
        """
        Testa a conectividade com a API do Ploomes.

        Returns:
            Tuple[bool, str]: (Sucesso?, Mensagem descritiva)
        """
        if not self.api_key:
            return False, "Chave de API (User-Key) não configurada."

        url = f"{self.base_url}/Tasks?$top=1"
        try:
            resp = requests.get(url, headers=self.headers, timeout=self.timeout)
            if resp.status_code == 200:
                return True, "Conexão com a API Ploomes estabelecida com sucesso."
            elif resp.status_code == 401 or resp.status_code == 403:
                return False, f"Falha de autenticação ({resp.status_code}): Verifique sua User-Key."
            else:
                return False, f"Erro retornado pela API ({resp.status_code}): {resp.text[:200]}"
        except requests.exceptions.RequestException as e:
            return False, f"Erro de rede ao conectar à API Ploomes: {e}"

    def get_total_tasks_count(self) -> int:
        """Retorna o número total de tarefas cadastradas no CRM."""
        url = f"{self.base_url}/Tasks?$top=1&$count=true"
        resp = requests.get(url, headers=self.headers, timeout=self.timeout)
        resp.raise_for_status()
        data = resp.json()
        return data.get("@odata.count", 0)

    def _execute_request_with_retry(self, url: str) -> requests.Response:
        """Executa requisição GET com tratamento de retries e backoff exponencial."""
        for attempt in range(1, self.max_retries + 1):
            try:
                resp = requests.get(url, headers=self.headers, timeout=self.timeout)
                # Retry em rate limit (429) ou erros temporários de servidor (5xx)
                if resp.status_code in [429, 500, 502, 503, 504]:
                    wait_time = 2 ** attempt
                    time.sleep(wait_time)
                    continue
                resp.raise_for_status()
                return resp
            except (requests.exceptions.ConnectionError, requests.exceptions.Timeout) as err:
                if attempt == self.max_retries:
                    raise err
                time.sleep(2 ** attempt)
        raise RuntimeError(f"Falha ao executar requisição para {url} após {self.max_retries} tentativas.")

    def fetch_all_tasks_raw(
        self,
        page_size: int = 300,
        progress_callback: Optional[Callable[[int, int, str], None]] = None
    ) -> List[Dict[str, Any]]:
        """
        Recupera todas as tarefas da API Ploomes paginando via OData.

        Args:
            page_size: Quantidade de registros por requisição (padrão: 300).
            progress_callback: Função callback(count_atual, total_estimado, mensagem).

        Returns:
            List[Dict[str, Any]]: Lista bruta com todas as tarefas em formato JSON.
        """
        if not self.api_key:
            raise ValueError("Chave de API do Ploomes (User-Key) não informada.")

        # Obtém total para feedback de progresso
        try:
            total_tasks = self.get_total_tasks_count()
        except Exception:
            total_tasks = 0

        skip = 0
        all_tasks: List[Dict[str, Any]] = []
        expand_fields = "Type,Contact,Deal,Creator,Users($expand=User),Tags($expand=Tag)"

        if progress_callback:
            progress_callback(0, total_tasks, "Conectando à API do Ploomes CRM...")

        while True:
            url = f"{self.base_url}/Tasks?$top={page_size}&$skip={skip}&$expand={expand_fields}&$orderby=Id asc"
            resp = self._execute_request_with_retry(url)
            data = resp.json()
            items = data.get("value", [])

            if not items:
                break

            all_tasks.extend(items)
            current_count = len(all_tasks)

            if progress_callback:
                progresso_pct = f"{int((current_count / total_tasks) * 100)}%" if total_tasks > 0 else f"{current_count} lidas"
                msg = f"Baixando tarefas... {current_count:,} de {total_tasks:,} ({progresso_pct})".replace(",", ".")
                progress_callback(current_count, total_tasks, msg)

            if len(items) < page_size:
                break

            skip += page_size

        return all_tasks

    def normalize_tasks_to_dataframe(self, raw_tasks: List[Dict[str, Any]]) -> pd.DataFrame:
        """
        Normaliza a lista de dicionários JSON retornada pela API Ploomes
        para um DataFrame com as colunas padronizadas exigidas pelo pipeline de ETL.
        Garante timezone-naive para compatibilidade estrita com o motor analítico.
        """
        records = []
        for t in raw_tasks:
            # 1. Usuários participantes
            user_names = []
            if t.get("Users"):
                for u in t["Users"]:
                    user_obj = u.get("User") if isinstance(u, dict) else None
                    if user_obj and user_obj.get("Name"):
                        user_names.append(str(user_obj["Name"]).strip())
            usuarios_str = ", ".join(user_names) if user_names else None

            # 2. Marcadores (Tags)
            tag_names = []
            if t.get("Tags"):
                for tag in t["Tags"]:
                    tag_obj = tag.get("Tag") if isinstance(tag, dict) else None
                    if tag_obj and tag_obj.get("Name"):
                        tag_names.append(str(tag_obj["Name"]).strip())
            marcadores_str = ", ".join(tag_names) if tag_names else None

            # 3. Cliente (Nome do Cliente / Contact)
            contact_name = None
            if t.get("Contact") and isinstance(t["Contact"], dict) and t["Contact"].get("Name"):
                contact_name = t["Contact"]["Name"]
            elif t.get("ContactName"):
                contact_name = t["ContactName"]

            # 4. Negócio (Deal)
            deal_title = None
            if t.get("Deal") and isinstance(t["Deal"], dict) and t["Deal"].get("Title"):
                deal_title = t["Deal"]["Title"]

            # 5. Tipo e Criador
            type_name = t.get("Type", {}).get("Name") if isinstance(t.get("Type"), dict) else None
            creator_name = t.get("Creator", {}).get("Name") if isinstance(t.get("Creator"), dict) else None
            creator_email = t.get("Creator", {}).get("Email") if isinstance(t.get("Creator"), dict) else None

            # 6. Conversão de datas para timezone-naive
            # O motor analítico exige que todas as datas sejam independentes de fuso horário (naive)
            dt_raw = t.get("DateTime")
            dt_val = None
            if dt_raw:
                parsed_dt = pd.to_datetime(dt_raw)
                # Remove o timezone caso exista de forma segura
                dt_val = parsed_dt.replace(tzinfo=None) if parsed_dt.tzinfo else parsed_dt

            create_dt_raw = t.get("CreateDate")
            create_dt_val = None
            if create_dt_raw:
                parsed_create_dt = pd.to_datetime(create_dt_raw)
                create_dt_val = parsed_create_dt.replace(tzinfo=None) if parsed_create_dt.tzinfo else parsed_create_dt

            # 7. Duração em minutos
            # Previne falhas caso a API retorne strings não numéricas no campo de duração
            length_val = t.get("Length")
            try:
                duracao_float = float(length_val) if length_val is not None else 0.0
            except (ValueError, TypeError):
                duracao_float = 0.0

            # 8. Objeto normalizado
            rec = {
                "Título": t.get("Title"),
                "Descrição": t.get("Description"),
                "Finalizada": bool(t.get("Finished")),
                "Data": dt_val,
                "Nome do Cliente": contact_name,
                "Título do Negócio": deal_title,
                "Usuários": usuarios_str,
                "Marcadores": marcadores_str,
                "Data de criação": create_dt_val,
                "Tipo": type_name,
                "Criador": creator_name,
                "Duração": duracao_float,
                "Cliente": contact_name,
                "Negócio": deal_title,
                "E-mail do criador (Google Calendar)": creator_email
            }
            records.append(rec)

        df = pd.DataFrame(records)
        return df

    def fetch_tasks_dataframe(
        self,
        page_size: int = 300,
        progress_callback: Optional[Callable[[int, int, str], None]] = None
    ) -> pd.DataFrame:
        """
        Executa o fluxo completo: busca todas as tarefas da API e normaliza em DataFrame.
        """
        raw_tasks = self.fetch_all_tasks_raw(page_size=page_size, progress_callback=progress_callback)
        if progress_callback:
            progress_callback(len(raw_tasks), len(raw_tasks), "Normalizando estrutura de dados colunar...")
        return self.normalize_tasks_to_dataframe(raw_tasks)


    def fetch_users_dimension(self) -> pd.DataFrame:
        """
        Consulta a tabela de usuários (/Users) da API Ploomes CRM
        e retorna uma dimensão cadastral enriquecida com flag de equipe comercial e status.
        """
        url = f"{self.base_url}/Users"
        resp = self._execute_request_with_retry(url)
        users = resp.json().get("value", [])

        try:
            from app.config.settings import is_commercial_user
        except Exception:
            def is_commercial_user(n):
                return True

        records = []
        for u in users:
            name = u.get("Name", "").strip()
            is_integration = bool(u.get("Integration", False))
            is_suspended = bool(u.get("Suspended", False))
            is_sales = is_commercial_user(name)

            records.append({
                "id_usuario": u.get("Id"),
                "nome_usuario": name,
                "email": u.get("Email"),
                "is_ativo": not is_suspended,
                "is_integracao": is_integration,
                "is_equipe_comercial": is_sales
            })
        return pd.DataFrame(records)


if __name__ == "__main__":
    client = PloomesClient()
    ok, msg = client.test_connection()
    print(f"Teste de Conexão: {msg}")
    if ok:
        total = client.get_total_tasks_count()
        print(f"Total de tarefas cadastradas no Ploomes: {total}")
        df_u = client.fetch_users_dimension()
        print(f"Total de usuários cadastrados: {len(df_u)}")
        print(df_u[["nome_usuario", "email", "is_ativo", "is_equipe_comercial"]])
