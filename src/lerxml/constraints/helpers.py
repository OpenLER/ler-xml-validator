def before_cutoff(feat: _Element) -> bool:
    etabelm = feat.find("ler:etableringstidspunkt", namespaces='ler')
    etabstr = etabelm.text
    etabdate = datetime.strptime(etabstr, "%Y-%m-%d")

    cutoff = datetime.strptime("2023-01-01", "%Y-%m-%d")
    return etabdate < cutoff

        