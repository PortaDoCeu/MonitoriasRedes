    segundos = time.perf_counter() - inicio
    print(dict(contadores))
    print(f"{contadores['capturados'] / segundos:.0f} segmentos/s")


if __name__ == "__main__":
    main()
